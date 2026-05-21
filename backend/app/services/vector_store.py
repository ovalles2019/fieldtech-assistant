from typing import Any

import chromadb
from chromadb.config import Settings as ChromaSettings

from app.config import settings
from app.models.schemas import Citation, DocumentType
from app.services.embeddings import embedding_service


class VectorStore:
    def __init__(self) -> None:
        self._client: chromadb.HttpClient | chromadb.Client | None = None
        self._collection = None

    def connect(self) -> None:
        try:
            self._client = chromadb.HttpClient(
                host=settings.chroma_host,
                port=settings.chroma_port,
                settings=ChromaSettings(anonymized_telemetry=False),
            )
            self._collection = self._client.get_or_create_collection(
                name=settings.chroma_collection,
                metadata={"hnsw:space": "cosine"},
            )
        except Exception:
            # Ephemeral local fallback when Docker not running
            self._client = chromadb.Client(ChromaSettings(anonymized_telemetry=False))
            self._collection = self._client.get_or_create_collection(
                name=settings.chroma_collection,
                metadata={"hnsw:space": "cosine"},
            )

    @property
    def collection(self):
        if self._collection is None:
            self.connect()
        return self._collection

    def upsert_chunks(
        self,
        ids: list[str],
        texts: list[str],
        metadatas: list[dict[str, Any]],
    ) -> None:
        embeddings = embedding_service.embed(texts)
        self.collection.upsert(ids=ids, documents=texts, embeddings=embeddings, metadatas=metadatas)

    def search(
        self,
        query: str,
        equipment_id: str | None = None,
        doc_types: list[DocumentType] | None = None,
        top_k: int = 6,
    ) -> list[Citation]:
        where: dict[str, Any] | None = None
        clauses: list[dict[str, Any]] = []
        if equipment_id:
            clauses.append({"equipment_id": {"$eq": equipment_id}})
        if doc_types:
            clauses.append({"doc_type": {"$in": [d.value for d in doc_types]}})
        if len(clauses) == 1:
            where = clauses[0]
        elif len(clauses) > 1:
            where = {"$and": clauses}

        query_embedding = embedding_service.embed_query(query)
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=where,
            include=["documents", "metadatas", "distances"],
        )

        citations: list[Citation] = []
        if not results["ids"] or not results["ids"][0]:
            return citations

        for i, doc_id in enumerate(results["ids"][0]):
            meta = results["metadatas"][0][i] if results["metadatas"] else {}
            dist = results["distances"][0][i] if results["distances"] else 1.0
            score = max(0.0, 1.0 - dist)
            citations.append(
                Citation(
                    document_id=meta.get("document_id", doc_id),
                    title=meta.get("title", "Unknown"),
                    doc_type=DocumentType(meta.get("doc_type", "manual")),
                    excerpt=(results["documents"][0][i] if results["documents"] else "")[:500],
                    page=meta.get("page"),
                    score=round(score, 3),
                )
            )
        return citations

    def count(self) -> int:
        return self.collection.count()

    def health_check(self) -> bool:
        try:
            self.connect()
            return self.collection is not None
        except Exception:
            return False


vector_store = VectorStore()
