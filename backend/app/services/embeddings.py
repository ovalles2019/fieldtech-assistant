from app.config import settings


class EmbeddingService:
    def __init__(self) -> None:
        self._openai = None

    @property
    def openai(self):
        if self._openai is None and settings.openai_api_key:
            from openai import OpenAI

            self._openai = OpenAI(api_key=settings.openai_api_key)
        return self._openai

    def embed(self, texts: list[str]) -> list[list[float]]:
        if self.openai:
            try:
                resp = self.openai.embeddings.create(model=settings.embedding_model, input=texts)
                return [d.embedding for d in resp.data]
            except Exception:
                pass
        return [_pseudo_embed(t) for t in texts]

    def embed_query(self, text: str) -> list[float]:
        return self.embed([text])[0]


def _pseudo_embed(text: str, dim: int = 384) -> list[float]:
    import hashlib
    import math

    h = hashlib.sha256(text.lower().encode()).digest()
    vec = []
    for i in range(dim):
        byte = h[i % len(h)]
        vec.append((byte / 255.0) * 2 - 1)
    norm = math.sqrt(sum(v * v for v in vec)) or 1.0
    return [v / norm for v in vec]


embedding_service = EmbeddingService()
