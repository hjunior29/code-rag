"""Consultas: busca semântica (pgvector), busca por símbolo e listagem de projetos."""

import logging

from app import db
from app.embeddings import get_embedder

logger = logging.getLogger(__name__)

MAX_CONTENT_CHARS = 4000


def _trim(content: str) -> str:
    if len(content) > MAX_CONTENT_CHARS:
        return content[:MAX_CONTENT_CHARS] + "\n... [truncado]"
    return content


async def search_code(
    query: str,
    project: str | None = None,
    lang: str | None = None,
    top_k: int = 10,
) -> list[dict]:
    """Busca semântica por linguagem natural sobre os chunks indexados."""
    top_k = max(1, min(int(top_k), 50))
    if not query.strip():
        return []
    if not await db.chunks_table_ready():
        return []

    embedder = get_embedder()
    qvec = db.vec_literal(await embedder.embed_query(query))

    sql = """
        SELECT p.name AS project, c.file_path, c.lang, c.kind, c.name,
               c.start_line, c.end_line, c.content,
               1 - (c.embedding <=> CAST($1 AS vector)) AS score
          FROM chunks c
          JOIN projects p ON p.id = c.project_id
         WHERE c.embedding IS NOT NULL
    """
    params: list = [qvec]
    if project:
        params.append(project)
        sql += f" AND p.name = ${len(params)}"
    if lang:
        params.append(lang.lower())
        sql += f" AND c.lang = ${len(params)}"
    sql += f" ORDER BY c.embedding <=> CAST($1 AS vector) LIMIT ${len(params) + 1}"
    params.append(top_k)

    pool = await db.get_pool()
    rows = await pool.fetch(sql, *params)
    return [
        {
            "project": r["project"],
            "file_path": r["file_path"],
            "lang": r["lang"],
            "kind": r["kind"],
            "name": r["name"],
            "start_line": r["start_line"],
            "end_line": r["end_line"],
            "score": round(float(r["score"]), 4),
            "content": _trim(r["content"]),
        }
        for r in rows
    ]


async def find_symbol(symbol: str, project: str | None = None, top_k: int = 20) -> list[dict]:
    """Busca exata/parcial por nome de símbolo (função, classe, método...)."""
    top_k = max(1, min(int(top_k), 100))
    if not symbol.strip() or not await db.chunks_table_ready():
        return []

    sql = """
        SELECT p.name AS project, c.file_path, c.lang, c.kind, c.name,
               c.start_line, c.end_line, c.content,
               (lower(c.name) = lower($1)) AS exact
          FROM chunks c
          JOIN projects p ON p.id = c.project_id
         WHERE c.name ILIKE '%' || $1 || '%'
    """
    params: list = [symbol.strip()]
    if project:
        params.append(project)
        sql += f" AND p.name = ${len(params)}"
    sql += f" ORDER BY exact DESC, length(c.name) ASC LIMIT ${len(params) + 1}"
    params.append(top_k)

    pool = await db.get_pool()
    rows = await pool.fetch(sql, *params)
    return [
        {
            "project": r["project"],
            "file_path": r["file_path"],
            "lang": r["lang"],
            "kind": r["kind"],
            "name": r["name"],
            "start_line": r["start_line"],
            "end_line": r["end_line"],
            "content": _trim(r["content"]),
        }
        for r in rows
    ]


async def list_projects() -> list[dict]:
    """Lista os projetos indexados e suas estatísticas."""
    await db.ensure_base_schema()
    pool = await db.get_pool()
    rows = await pool.fetch(
        """
        SELECT name, root_path, file_count, chunk_count, last_indexed_at
          FROM projects ORDER BY name
        """
    )
    return [
        {
            "name": r["name"],
            "root_path": r["root_path"],
            "file_count": r["file_count"],
            "chunk_count": r["chunk_count"],
            "last_indexed_at": r["last_indexed_at"].isoformat() if r["last_indexed_at"] else None,
        }
        for r in rows
    ]


async def list_langs() -> list[str]:
    if not await db.chunks_table_ready():
        return []
    pool = await db.get_pool()
    rows = await pool.fetch("SELECT DISTINCT lang FROM chunks ORDER BY lang")
    return [r["lang"] for r in rows]
