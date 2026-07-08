"""Pool asyncpg + criação de schema.

O schema é criado em duas etapas porque a dimensão do vetor só é conhecida
após o primeiro embedding (auto-detecção):
  1. ensure_base_schema(): extensão vector + tabelas projects/meta (no boot do servidor)
  2. ensure_chunks_table(dim, model): tabela chunks com vector(dim) (na primeira indexação)
"""

import logging

import asyncpg

from app.config import settings

logger = logging.getLogger(__name__)

_pool: asyncpg.Pool | None = None

# HNSW do pgvector suporta no máximo 2000 dimensões
HNSW_MAX_DIM = 2000


async def get_pool() -> asyncpg.Pool:
    global _pool
    if _pool is None:
        _pool = await asyncpg.create_pool(settings.DATABASE_URL, min_size=1, max_size=8)
    return _pool


async def close_pool() -> None:
    global _pool
    if _pool is not None:
        await _pool.close()
        _pool = None


async def ensure_base_schema() -> None:
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
        await conn.execute(
            """
            CREATE TABLE IF NOT EXISTS projects (
                id BIGSERIAL PRIMARY KEY,
                name TEXT NOT NULL UNIQUE,
                root_path TEXT NOT NULL,
                file_count INT NOT NULL DEFAULT 0,
                chunk_count INT NOT NULL DEFAULT 0,
                last_indexed_at TIMESTAMPTZ
            )
            """
        )
        await conn.execute(
            """
            CREATE TABLE IF NOT EXISTS meta (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
            """
        )


async def get_meta(key: str) -> str | None:
    pool = await get_pool()
    return await pool.fetchval("SELECT value FROM meta WHERE key = $1", key)


async def set_meta(key: str, value: str) -> None:
    pool = await get_pool()
    await pool.execute(
        "INSERT INTO meta (key, value) VALUES ($1, $2) ON CONFLICT (key) DO UPDATE SET value = $2",
        key,
        value,
    )


async def chunks_table_ready() -> bool:
    return await get_meta("embedding_dim") is not None


async def ensure_chunks_table(dim: int, model: str) -> None:
    """Cria a tabela chunks com a dimensão detectada, ou valida a existente."""
    await ensure_base_schema()
    existing_dim = await get_meta("embedding_dim")
    existing_model = await get_meta("embedding_model")

    if existing_dim is not None:
        if int(existing_dim) != dim or existing_model != model:
            raise RuntimeError(
                f"Banco foi indexado com modelo '{existing_model}' (dim={existing_dim}), "
                f"mas a config atual é '{model}' (dim={dim}). "
                "Embeddings de modelos diferentes são incompatíveis. "
                "Rode 'make reset-db' e reindexe tudo, ou volte a config anterior."
            )
        return

    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS chunks (
                id BIGSERIAL PRIMARY KEY,
                project_id BIGINT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
                file_path TEXT NOT NULL,
                lang TEXT NOT NULL,
                kind TEXT NOT NULL,
                name TEXT,
                start_line INT NOT NULL,
                end_line INT NOT NULL,
                content TEXT NOT NULL,
                content_sha TEXT NOT NULL,
                embedding vector({dim})
            )
            """
        )
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_chunks_project ON chunks (project_id)")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_chunks_name ON chunks (name)")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_chunks_sha ON chunks (project_id, content_sha)")
        if dim <= HNSW_MAX_DIM:
            await conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_chunks_embedding_hnsw "
                "ON chunks USING hnsw (embedding vector_cosine_ops)"
            )
        else:
            logger.warning(
                "dim=%d excede o limite HNSW (%d); busca usará scan sequencial (ok para escala local)",
                dim,
                HNSW_MAX_DIM,
            )
    await set_meta("embedding_dim", str(dim))
    await set_meta("embedding_model", model)


def vec_literal(vec: list[float]) -> str:
    """Formata um vetor como literal pgvector: '[0.1,0.2,...]'."""
    return "[" + ",".join(f"{x:.8f}" for x in vec) + "]"
