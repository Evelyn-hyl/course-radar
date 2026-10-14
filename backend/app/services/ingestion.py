from pathlib import Path
from tempfile import TemporaryDirectory

from fastapi import UploadFile

from app.ingestion.pipeline import IngestionResult, ingest_pdf


MAX_UPLOAD_BYTES = 25 * 1024 * 1024
READ_SIZE = 1024 * 1024


class InvalidUploadError(ValueError):
    """Raised when an uploaded file is not an acceptable PDF."""


class IngestionService:
    async def ingest(self, upload: UploadFile) -> IngestionResult:
        filename = upload.filename or ""

        if Path(filename).suffix.lower() != ".pdf":
            raise InvalidUploadError("Only .pdf files are supported.")
        
        if upload.content_type not in (None, "application/pdf"):
            raise InvalidUploadError("The upload must have content type application/pdf.")

        with TemporaryDirectory(prefix="courseradar-") as directory:
            pdf_path = Path(directory) / "upload.pdf"
            total_bytes = 0
            signature = b""

            with pdf_path.open("wb") as destination:
                while data := await upload.read(READ_SIZE):
                    if not signature:
                        signature = data[:5]
                    total_bytes += len(data)
                    if total_bytes > MAX_UPLOAD_BYTES:
                        raise InvalidUploadError("PDF exceeds the 25 MB upload limit.")
                    destination.write(data)

            if signature != b"%PDF-":
                raise InvalidUploadError("The uploaded file is not a valid PDF.")

            return ingest_pdf(pdf_path)


def get_ingestion_service() -> IngestionService:
    return IngestionService()
