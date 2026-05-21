from fastapi import APIRouter, Depends, File, Form, UploadFile

from app.auth.cognito import CurrentUser, get_current_user
from app.models.schemas import DocumentType, IngestRequest
from app.services.ingest import ingest_service

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.post("/ingest")
async def ingest_document(
    title: str = Form(...),
    doc_type: DocumentType = Form(...),
    equipment_id: str | None = Form(None),
    file: UploadFile = File(...),
    user: CurrentUser = Depends(get_current_user),
) -> dict:
    _ = user
    data = await file.read()
    from tempfile import NamedTemporaryFile
    from pathlib import Path

    suffix = Path(file.filename or "upload.txt").suffix
    with NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(data)
        tmp_path = Path(tmp.name)

    from app.services.document_parser import parse_file

    text = parse_file(tmp_path, data)
    doc_id = ingest_service.ingest_text(title, text, doc_type, equipment_id)
    tmp_path.unlink(missing_ok=True)
    return {"document_id": doc_id, "chunks_indexed": True}
