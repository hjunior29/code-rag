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


# Sub-batch pequeno: limita o pico de memória do ONNX (atenção cresce
# quadraticamente com o tamanho do batch × sequência)
_ONNX_BATCH = 16


class FastembedEmbedder(Embedder):
    def __init__(self) -> None:
        self._model = None
        self._lock = asyncio.Lock()
        # ONNX já paraleliza internamente entre os cores; chamadas concorrentes
        # só multiplicariam o uso de memória (causa de OOM em VMs pequenas)
        self._run_lock = asyncio.Semaphore(1)

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
        async with self._run_lock:
            vectors = await loop.run_in_executor(
                None, lambda: list(model.embed(texts, batch_size=_ONNX_BATCH))
            )
        return [v.tolist() for v in vectors]
