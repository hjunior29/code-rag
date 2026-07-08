"""Embedder via API OpenAI-compatible.

Cobre OpenAI oficial e qualquer servidor que fale o mesmo protocolo:
LM Studio, vLLM, llama.cpp server, Together, Fireworks, etc. — basta
apontar OPENAI_BASE_URL e OPENAI_API_KEY."""

import httpx

from app.config import settings
from app.embeddings.base import Embedder


class OpenAICompatEmbedder(Embedder):
    def __init__(self) -> None:
        headers = {}
        if settings.OPENAI_API_KEY:
            headers["Authorization"] = f"Bearer {settings.OPENAI_API_KEY}"
        self._client = httpx.AsyncClient(
            base_url=settings.OPENAI_BASE_URL.rstrip("/"), headers=headers, timeout=300.0
        )

    async def _embed_one_batch(self, texts: list[str]) -> list[list[float]]:
        resp = await self._client.post(
            "/embeddings",
            json={"model": settings.EMBEDDING_MODEL, "input": texts},
        )
        resp.raise_for_status()
        data = resp.json()["data"]
        # A API garante ordem via index
        data.sort(key=lambda d: d["index"])
        return [d["embedding"] for d in data]
