from typing import Annotated

from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status

from app.domain.documents import SourceType
from app.embeddings.client import EmbeddingGenerationError
from app.ingestion.chunker import PdfChunkingError
from app.schemas.documents import (
    DocumentUploadMetadata,
    IngestedChunkResponse,
    IngestionPreviewResponse,
)
from app.services.ingestion import (
    CourseNotFoundError,
    DuplicateDocumentError,
    IngestionService,
    InvalidUploadError,
    get_ingestion_service,
)


router = APIRouter(prefix="/documents", tags=["documents"])


@router.post(
    "",
    response_model=IngestionPreviewResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_document(
    file: Annotated[UploadFile, File(description="PDF course material")],
    course_id: Annotated[UUID, Form()],
    title: Annotated[str, Form(min_length=1, max_length=255)],
    source_type: Annotated[SourceType, Form()],
    service: Annotated[IngestionService, Depends(get_ingestion_service)],
    week: Annotated[int | None, Form(ge=1)] = None,
) -> IngestionPreviewResponse:
    try:
        result = await service.ingest(
            file,
            DocumentUploadMetadata(
                course_id=course_id,
                title=title,
                source_type=source_type,
                week=week,
            ),
        )
    except InvalidUploadError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    except CourseNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except DuplicateDocumentError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error
    except PdfChunkingError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    except EmbeddingGenerationError as error:
        raise HTTPException(status_code=502, detail=str(error)) from error
    finally:
        await file.close()

    return IngestionPreviewResponse(
        document_id=result.document.id,
        status=result.document.status,
        page_count=result.ingestion.page_count,
        chunk_count=len(result.ingestion.chunks),
        chunks=[
            IngestedChunkResponse(
                text=chunk.text,
                page_start=chunk.page_start,
                page_end=chunk.page_end,
                section_path=list(chunk.section_path),
                content_types=list(chunk.content_types),
            )
            for chunk in result.ingestion.chunks
        ],
    )
