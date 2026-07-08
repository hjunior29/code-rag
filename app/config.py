"""Configuração central via variáveis de ambiente (.env)."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # --- Banco ---
    DATABASE_URL: str = "postgresql://coderag:coderag@postgres:5432/coderag"

    # --- Embeddings (agnóstico: escolha o provider e o modelo) ---
    # Providers: "fastembed" (in-process, ONNX) | "ollama" | "openai" (compatible) | "gemini"
    EMBEDDING_PROVIDER: str = "fastembed"
    EMBEDDING_MODEL: str = "BAAI/bge-small-en-v1.5"
    EMBEDDING_BATCH_SIZE: int = 64
    # Batches embedados em paralelo (vale para todos os providers)
    EMBEDDING_CONCURRENCY: int = 4
    # Alguns modelos (ex.: nomic-embed-text) melhoram com prefixos de tarefa.
    # Ex.: EMBEDDING_DOC_PREFIX="search_document: " / EMBEDDING_QUERY_PREFIX="search_query: "
    EMBEDDING_DOC_PREFIX: str = ""
    EMBEDDING_QUERY_PREFIX: str = ""

    # ollama
    OLLAMA_URL: str = "http://ollama:11434"

    # openai-compatible (OpenAI, LM Studio, vLLM, Together, etc.)
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"
    OPENAI_API_KEY: str = ""

    # gemini (REST direto, sem SDK)
    GEMINI_API_KEY: str = ""
    GEMINI_OUTPUT_DIM: int = 0  # 0 = dimensão nativa do modelo

    # --- Servidor ---
    HTTP_PORT: int = 8000

    # --- Indexação ---
    MAX_FILE_SIZE_KB: int = 512
    CHUNK_MAX_CHARS: int = 8000
    GENERIC_CHUNK_LINES: int = 100
    GENERIC_CHUNK_OVERLAP: int = 15


settings = Settings()
