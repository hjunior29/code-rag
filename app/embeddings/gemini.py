"""Embedder via Google Gemini (REST direto, sem SDK do Google).

Útil se você quiser a mesma qualidade do setup original em nuvem —
mas o padrão do projeto é local (ollama)."""

import httpx

from app.config import settings
from app.embeddings.base import Embedder

_BASE = "https://generativelanguage.googleapis.com/v1beta"


class GeminiEmbedder(Embedder):
    def __init__(self) -> None:
        if not settings.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY é obrigatório com EMBEDDING_PROVIDER=gemini")
        self._client = httpx.AsyncClient(base_url=_BASE, timeout=300.0)

    async def _embed_one_batch(self, texts: list[str]) -> list[list[float]]:
        model = settings.EMBEDDING_MODEL
        if not model.startswith("models/"):
            model = f"models/{model}"
        requests = []
        for text in texts:
            req: dict = {"model": model, "content": {"parts": [{"text": text}]}}
            if settings.GEMINI_OUTPUT_DIM > 0:
                req["outputDimensionality"] = settings.GEMINI_OUTPUT_DIM
            requests.append(req)
        resp = await self._client.post(
            f"/{model}:batchEmbedContents",
            params={"key": settings.GEMINI_API_KEY},
            json={"requests": requests},
        )
        resp.raise_for_status()
        return [e["values"] for e in resp.json()["embeddings"]]
