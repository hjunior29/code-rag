"""Dispatch de chunking: tree-sitter quando há gramática, senão janela de linhas."""

from pathlib import Path

from app.config import settings
from app.indexer.chunkers.base import Chunk
from app.indexer.chunkers.generic import EXT_TO_LANG, FILENAME_TO_LANG, chunk_generic
from app.indexer.chunkers.treesitter import EXT_TO_TS_LANG, chunk_with_treesitter


def chunk_file(text: str, rel_path: str) -> list[Chunk]:
    path = Path(rel_path)
    ext = path.suffix.lower()

    chunks: list[Chunk] = []
    ts_lang = EXT_TO_TS_LANG.get(ext)
    if ts_lang is not None:
        chunks = chunk_with_treesitter(text, rel_path, ts_lang)
        lang = "typescript" if ts_lang == "tsx" else ts_lang
    else:
        lang = FILENAME_TO_LANG.get(path.name) or EXT_TO_LANG.get(ext, "text")

    # Arquivo sem símbolos extraídos (script solto, config, etc.) → chunk genérico
    if not chunks:
        chunks = chunk_generic(text, rel_path, lang)

    # Trava de segurança: corta conteúdo gigante (uma função de 3000 linhas ainda entra, truncada)
    for chunk in chunks:
        if len(chunk.content) > settings.CHUNK_MAX_CHARS:
            chunk.content = chunk.content[: settings.CHUNK_MAX_CHARS]
    return chunks
