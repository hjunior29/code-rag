"""Embedder via Ollama (roda 100% local). Funciona com qualquer modelo de
embedding que o Ollama sirva: nomic-embed-text, mxbai-embed-large,
snowflake-arctic-embed, bge-m3, etc."""

import httpx

from app.config import settings
from app.embeddings.base import Embedder


class OllamaEmbedder(Embedder):
    def __init__(self) -> None:
        self._client = httpx.AsyncClient(base_url=settings.OLLAMA_URL, timeout=300.0)

    async def _embed_one_batch(self, texts: list[str]) -> list[list[float]]:
        resp = await self._client.post(
            "/api/embed",
            json={"model": settings.EMBEDDING_MODEL, "input": texts},
        )
        resp.raise_for_status()
        data = resp.json()
        return data["embeddings"]
