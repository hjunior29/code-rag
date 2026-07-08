"""Interface comum de embedders + retry com backoff exponencial."""

import abc
import asyncio
import logging
import random

from app.config import settings

logger = logging.getLogger(__name__)

MAX_RETRIES = 5


class Embedder(abc.ABC):
    """Contrato único: uma lista de textos entra, uma lista de vetores sai."""

    @abc.abstractmethod
    async def _embed_one_batch(self, texts: list[str]) -> list[list[float]]:
        """Embeda um único batch (já do tamanho certo). Implementado por provider."""

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Embeda qualquer quantidade de textos: quebra em batches e processa
        até EMBEDDING_CONCURRENCY batches em paralelo, com retry individual.
        A ordem dos vetores retornados corresponde à ordem dos textos."""
        if not texts:
            return []
        batch_size = settings.EMBEDDING_BATCH_SIZE
        batches = [texts[i : i + batch_size] for i in range(0, len(texts), batch_size)]
        semaphore = asyncio.Semaphore(max(1, settings.EMBEDDING_CONCURRENCY))

        async def run(batch: list[str]) -> list[list[float]]:
            async with semaphore:
                return await self._with_retry(batch)

        results = await asyncio.gather(*(run(b) for b in batches))
        return [vec for batch_vecs in results for vec in batch_vecs]

    async def embed_query(self, query: str) -> list[float]:
        vecs = await self.embed_batch([settings.EMBEDDING_QUERY_PREFIX + query])
        return vecs[0]

    async def detect_dim(self) -> int:
        """Auto-detecta a dimensão do modelo configurado embedando um texto de prova."""
        vecs = await self._with_retry(["dimension probe"])
        return len(vecs[0])

    async def _with_retry(self, texts: list[str]) -> list[list[float]]:
        for attempt in range(MAX_RETRIES + 1):
            try:
                result = await self._embed_one_batch(texts)
                if len(result) != len(texts):
                    raise RuntimeError(f"provider retornou {len(result)} vetores para {len(texts)} textos")
                return result
            except Exception as exc:
                if attempt >= MAX_RETRIES:
                    logger.error("embedder desistiu após %d tentativas: %s", attempt, exc)
                    raise
                delay = (2**attempt) + random.random()
                logger.warning("embedder retry %d em %.1fs: %s", attempt + 1, delay, exc)
                await asyncio.sleep(delay)
        raise RuntimeError("unreachable")
