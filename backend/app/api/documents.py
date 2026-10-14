from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from app.ingestion.chunker import PdfChunkingError
from app.schemas.documents import IngestedChunkResponse, IngestionPreviewResponse
from app.services.ingestion import (
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
    service: Annotated[IngestionService, Depends(get_ingestion_service)],
) -> IngestionPreviewResponse:
    try:
        result = await service.ingest(file)
    except InvalidUploadError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    except PdfChunkingError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    finally:
        await file.close()

    return IngestionPreviewResponse(
        page_count=result.page_count,
        chunk_count=len(result.chunks),
        chunks=[
            IngestedChunkResponse(
                text=chunk.text,
                page_start=chunk.page_start,
                page_end=chunk.page_end,
                section_path=list(chunk.section_path),
                content_types=list(chunk.content_types),
            )
            for chunk in result.chunks
        ],
    )
