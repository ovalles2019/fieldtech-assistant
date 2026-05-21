import uuid
from pathlib import Path

from app.models.schemas import DocumentType
from app.services.document_parser import build_chunk_metadata, chunk_text, parse_file
from app.services.storage import storage_service
from app.services.vector_store import vector_store


class IngestService:
    def ingest_text(
        self,
        title: str,
        text: str,
        doc_type: DocumentType,
        equipment_id: str | None,
        s3_key: str | None = None,
    ) -> str:
        document_id = str(uuid.uuid4())
        key = s3_key or f"manuals/{equipment_id or 'global'}/{document_id}.txt"
        storage_service.upload_bytes(key, text.encode("utf-8"), "text/plain")

        chunks = chunk_text(text)
        ids = []
        texts = []
        metas = []
        for i, chunk in enumerate(chunks):
            chunk_id = f"{document_id}::{i}"
            ids.append(chunk_id)
            texts.append(chunk)
            metas.append(
                build_chunk_metadata(document_id, title, doc_type, equipment_id, page=None, chunk_index=i)
            )

        if ids:
            vector_store.upsert_chunks(ids, texts, metas)
        return document_id

    def ingest_file_path(
        self,
        path: Path,
        title: str,
        doc_type: DocumentType,
        equipment_id: str | None,
    ) -> str:
        text = parse_file(path)
        key = f"manuals/{equipment_id or 'global'}/{path.name}"
        storage_service.upload_bytes(key, text.encode("utf-8"), "text/plain")
        return self.ingest_text(title, text, doc_type, equipment_id, s3_key=key)


ingest_service = IngestService()
