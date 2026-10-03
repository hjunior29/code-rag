"""Pipeline de indexação: walk → chunk → dedup por sha → embed → gravar.

Reindexações são baratas: chunks cujo conteúdo não mudou reutilizam o
embedding já existente no banco (dedup por content_sha), então só o que
mudou vai para o provider de embeddings.
"""

import hashlib
import logging
import time
from pathlib import Path

from tqdm import tqdm

from app import db
from app.config import settings
from app.embeddings import get_embedder
from app.indexer.chunkers import chunk_file
from app.indexer.chunkers.base import Chunk
from app.indexer.walker import read_text, walk_files

logger = logging.getLogger(__name__)

_BAR_FMT = "{desc:<12} {percentage:3.0f}%|{bar:40}| {n_fmt}/{total_fmt} [{elapsed}<{remaining} {rate_fmt}]"


def _embed_text(chunk: Chunk) -> str:
    header = f"{chunk.file_path}\n{chunk.name or ''}\n"
    return (settings.EMBEDDING_DOC_PREFIX + header + chunk.content)[: settings.CHUNK_MAX_CHARS]


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


async def index_path(root: str, name: str, display_path: str | None = None) -> dict:
    started = time.monotonic()
    root_path = Path(root).resolve()
    if not root_path.is_dir():
        raise SystemExit(f"Diretório não encontrado: {root_path}")

    await db.ensure_base_schema()

    # 1. Walk + chunk
    tqdm.write(f"⚡ indexando '{name}' ({display_path or root_path})")
    files = walk_files(root_path)

    chunks: list[Chunk] = []
    parsed_files = 0
    for path in tqdm(files, desc="📂 parsing", unit="arq", bar_format=_BAR_FMT, colour="cyan"):
        text = read_text(path)
        if text is None or not text.strip():
            continue
        rel = str(path.relative_to(root_path))
        chunks.extend(chunk_file(text, rel))
        parsed_files += 1
    tqdm.write(f"   {len(chunks)} chunks extraídos de {parsed_files} arquivos")

    if not chunks:
        raise SystemExit("Nenhum chunk extraído — o diretório tem código-fonte?")

    # 2. Detecta a dimensão do modelo e garante o schema
    embedder = get_embedder()
    dim = await embedder.detect_dim()
    tqdm.write(f"   modelo: {settings.EMBEDDING_MODEL} ({settings.EMBEDDING_PROVIDER}, dim={dim})")
    await db.ensure_chunks_table(dim, settings.EMBEDDING_MODEL)

    # 3. Dedup: reutiliza embeddings de conteúdo inalterado (índice anterior
    #    do projeto + checkpoints de execuções interrompidas)
    pool = await db.get_pool()
    shas = [_sha(_embed_text(c)) for c in chunks]
    project_id = await pool.fetchval("SELECT id FROM projects WHERE name = $1", name)
    reusable: dict[str, str] = {}
    if project_id is not None:
        rows = await pool.fetch(
            "SELECT DISTINCT ON (content_sha) content_sha, embedding::text AS emb "
            "FROM chunks WHERE project_id = $1 AND embedding IS NOT NULL",
            project_id,
        )
        reusable = {r["content_sha"]: r["emb"] for r in rows}
    cache_rows = await pool.fetch("SELECT content_sha, embedding::text AS emb FROM embedding_cache")
    reusable.update({r["content_sha"]: r["emb"] for r in cache_rows})

    to_embed = [(i, _embed_text(chunks[i])) for i, sha in enumerate(shas) if sha not in reusable]
    tqdm.write(f"   {len(to_embed)} chunks novos para embedar ({len(chunks) - len(to_embed)} reutilizados ♻️)")

    # 4. Embed em grupos de batches paralelos, com progresso
    embeddings: dict[int, str] = {}
    group_size = settings.EMBEDDING_BATCH_SIZE * max(1, settings.EMBEDDING_CONCURRENCY)
    with tqdm(
        total=len(to_embed), desc="🧮 embeddings", unit="chunk", bar_format=_BAR_FMT, colour="green"
    ) as bar:
        for offset in range(0, len(to_embed), group_size):
            group = to_embed[offset : offset + group_size]
            vecs = await embedder.embed_batch([t for _, t in group])
            checkpoint: list[tuple[str, str]] = []
            for (idx, _), vec in zip(group, vecs):
                lit = db.vec_literal(vec)
                embeddings[idx] = lit
                checkpoint.append((shas[idx], lit))
            # Persiste o progresso: interrupção não perde o que já foi embedado
            await pool.executemany(
                "INSERT INTO embedding_cache (content_sha, embedding) VALUES ($1, $2::vector) "
                "ON CONFLICT (content_sha) DO NOTHING",
                checkpoint,
            )
            bar.update(len(group))

    # 5. Grava tudo numa transação (substitui o índice antigo do projeto)
    async with pool.acquire() as conn, conn.transaction():
        project_id = await conn.fetchval(
            """
            INSERT INTO projects (name, root_path, file_count, chunk_count, last_indexed_at)
            VALUES ($1, $2, $3, $4, now())
            ON CONFLICT (name) DO UPDATE
               SET root_path = $2, file_count = $3, chunk_count = $4, last_indexed_at = now()
            RETURNING id
            """,
            name,
            display_path or str(root_path),
            parsed_files,
            len(chunks),
        )
        await conn.execute("DELETE FROM chunks WHERE project_id = $1", project_id)
        rows = [
            (
                project_id,
                c.file_path,
                c.lang,
                c.kind,
                c.name,
                c.start_line,
                c.end_line,
                c.content,
                shas[i],
                embeddings.get(i) or reusable.get(shas[i]),
            )
            for i, c in enumerate(chunks)
        ]
        await conn.executemany(
            """
            INSERT INTO chunks
                (project_id, file_path, lang, kind, name, start_line, end_line, content, content_sha, embedding)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10::vector)
            """,
            rows,
        )

    # Índice gravado com sucesso: os checkpoints deste projeto não são mais necessários
    await pool.execute("DELETE FROM embedding_cache WHERE content_sha = ANY($1::text[])", list(set(shas)))

    elapsed = time.monotonic() - started
    summary = {
        "project": name,
        "files": parsed_files,
        "chunks": len(chunks),
        "embedded": len(to_embed),
        "reused": len(chunks) - len(to_embed),
        "seconds": round(elapsed, 1),
    }
    mins, secs = divmod(int(elapsed), 60)
    tqdm.write(f"✅ '{name}' indexado: {len(chunks)} chunks em {mins}m{secs:02d}s")
    return summary
