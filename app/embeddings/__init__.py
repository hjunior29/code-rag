"""Camada de embeddings agnóstica.

O provider é escolhido por EMBEDDING_PROVIDER — nenhum modelo específico é
assumido. Todos falam a mesma interface: embed_batch(texts) -> vetores.
"""

from app.config import settings
from app.embeddings.base import Embedder


def get_embedder() -> Embedder:
    provider = settings.EMBEDDING_PROVIDER.lower().strip()

    if provider == "fastembed":
        from app.embeddings.fastembed_local import FastembedEmbedder

        return FastembedEmbedder()
    elif provider == "ollama":
        from app.embeddings.ollama import OllamaEmbedder

        return OllamaEmbedder()
    elif provider in ("openai", "openai-compatible", "openai_compatible"):
        from app.embeddings.openai_compat import OpenAICompatEmbedder

        return OpenAICompatEmbedder()
    elif provider == "gemini":
        from app.embeddings.gemini import GeminiEmbedder

        return GeminiEmbedder()
    else:
        raise ValueError(
            f"EMBEDDING_PROVIDER desconhecido: '{provider}'. "
            "Use: fastembed | ollama | openai | gemini"
        )
