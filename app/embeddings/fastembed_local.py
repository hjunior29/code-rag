"""Embedder in-process via fastembed (ONNX, CPU) — zero serviços externos.

O modelo é baixado do Hugging Face na primeira execução e cacheado em disco.
Funciona com qualquer modelo suportado pelo fastembed, ex.:
  BAAI/bge-small-en-v1.5 (384d, leve e rápido)
  jinaai/jina-embeddings-v2-base-code (768d, especializado em código)
  BAAI/bge-base-en-v1.5, sentence-transformers/all-MiniLM-L6-v2, ...
"""

import asyncio

from app.config import settings
from app.embeddings.base import Embedder


class FastembedEmbedder(Embedder):
    def __init__(self) -> None:
        self._model = None
        self._lock = asyncio.Lock()

    async def _get_model(self):
        if self._model is None:
            async with self._lock:
                if self._model is None:
                    import os

                    from fastembed import TextEmbedding

                    loop = asyncio.get_running_loop()
                    self._model = await loop.run_in_executor(
                        None,
                        lambda: TextEmbedding(
                            model_name=settings.EMBEDDING_MODEL,
                            threads=os.cpu_count(),
                        ),
                    )
        return self._model

    async def _embed_one_batch(self, texts: list[str]) -> list[list[float]]:
        model = await self._get_model()
        loop = asyncio.get_running_loop()
        vectors = await loop.run_in_executor(None, lambda: list(model.embed(texts)))
        return [v.tolist() for v in vectors]
