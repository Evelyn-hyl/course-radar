import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Annotated
from uuid import uuid4

from fastapi import Depends, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Course, Document
from app.db.session import get_session
from app.domain.documents import DocumentStatus
from app.embeddings.client import EmbeddingClient, get_embedding_client
from app.ingestion.pipeline import IngestionResult, ingest_pdf
from app.repositories.documents import DocumentRepository
from app.schemas.documents import DocumentUploadMetadata


MAX_UPLOAD_BYTES = 25 * 1024 * 1024
READ_SIZE = 1024 * 1024


class InvalidUploadError(ValueError):
    """Raised when an uploaded file is not an acceptable PDF."""


class CourseNotFoundError(LookupError):
    """Raised when ingestion targets a course that does not exist."""


class DuplicateDocumentError(ValueError):
    """Raised when the course already contains the same PDF bytes."""


@dataclass(frozen=True, slots=True)
class StoredIngestionResult:
    document: Document
    ingestion: IngestionResult


class IngestionService:
    def __init__(
        self,
        session: Session,
        embedding_client: EmbeddingClient,
        *,
        storage_root: Path | None = None,
    ) -> None:
        self._session = session
        self._embedding_client = embedding_client
        backend_directory = Path(__file__).resolve().parents[2]
        self._storage_root = storage_root or backend_directory / "data" / "uploads"

    async def ingest(
        self,
        upload: UploadFile,
        metadata: DocumentUploadMetadata,
    ) -> StoredIngestionResult:
        filename = upload.filename or ""

        if Path(filename).suffix.lower() != ".pdf":
            raise InvalidUploadError("Only .pdf files are supported.")
        
        if upload.content_type not in (None, "application/pdf"):
            raise InvalidUploadError("The upload must have content type application/pdf.")

        if self._session.get(Course, metadata.course_id) is None:
            raise CourseNotFoundError(f"Course does not exist: {metadata.course_id}")

        document_id = uuid4()

        relative_path = (
            Path("data")
            / "uploads"
            / str(metadata.course_id)
            / f"{document_id}.pdf"
        )

        pdf_path = self._storage_root / str(metadata.course_id) / f"{document_id}.pdf"

        try:
            checksum = await self._save_upload(upload, pdf_path)

            duplicate = self._session.scalar(
                select(Document.id).where(
                    Document.course_id == metadata.course_id,
                    Document.checksum == checksum,
                )
            )

            if duplicate is not None:
                raise DuplicateDocumentError(
                    "This PDF has already been uploaded to the course."
                )

            document = Document(
                id=document_id,
                course_id=metadata.course_id,
                title=metadata.title,
                source_type=metadata.source_type,
                path=relative_path.as_posix(),
                checksum=checksum,
                status=DocumentStatus.PROCESSING,
                week=metadata.week,
            )

            self._session.add(document)
            self._session.flush()

            ingestion = ingest_pdf(pdf_path)

            embeddings = await self._embedding_client.embed_documents(
                [chunk.text for chunk in ingestion.chunks]
            )

            DocumentRepository(self._session).add_chunks(
                document_id=document.id,
                chunks=ingestion.chunks,
                embeddings=embeddings,
                embedding_model=self._embedding_client.model,
            )

            document.status = DocumentStatus.READY
            self._session.commit()
            self._session.refresh(document)

            return StoredIngestionResult(document, ingestion)
        except Exception:
            self._session.rollback()
            pdf_path.unlink(missing_ok=True)
            raise

    async def _save_upload(self, upload: UploadFile, pdf_path: Path) -> str:
        pdf_path.parent.mkdir(parents=True, exist_ok=True)

        total_bytes = 0
        signature = b""
        checksum = hashlib.sha256()

        with pdf_path.open("xb") as destination:
            while data := await upload.read(READ_SIZE):
                if not signature:
                    signature = data[:5]

                total_bytes += len(data)

                if total_bytes > MAX_UPLOAD_BYTES:
                    raise InvalidUploadError("PDF exceeds the 25 MB upload limit.")

                checksum.update(data)
                destination.write(data)

        if signature != b"%PDF-":
            raise InvalidUploadError("The uploaded file is not a valid PDF.")

        return checksum.hexdigest()


def get_ingestion_service(
    session: Annotated[Session, Depends(get_session)],
    embedding_client: Annotated[EmbeddingClient, Depends(get_embedding_client)],
) -> IngestionService:
    return IngestionService(session, embedding_client)
