"""Chunker genérico por janela de linhas — fallback para qualquer linguagem
sem gramática tree-sitter instalada (Rust, Java, Vue, SQL, Markdown, etc.)."""

from app.config import settings
from app.indexer.chunkers.base import Chunk

# Mapeia extensão -> rótulo de linguagem para filtros de busca
EXT_TO_LANG = {
    ".md": "markdown", ".mdx": "markdown", ".rst": "markdown", ".txt": "text",
    ".json": "json", ".yaml": "yaml", ".yml": "yaml", ".toml": "toml",
    ".ini": "config", ".cfg": "config", ".conf": "config",
    ".sql": "sql", ".graphql": "graphql", ".proto": "proto", ".prisma": "prisma",
    ".sh": "shell", ".bash": "shell", ".zsh": "shell", ".fish": "shell", ".ps1": "powershell",
    ".rb": "ruby", ".rs": "rust", ".java": "java", ".kt": "kotlin", ".kts": "kotlin",
    ".scala": "scala", ".php": "php",
    ".c": "c", ".h": "c", ".cpp": "cpp", ".hpp": "cpp", ".cc": "cpp", ".hh": "cpp",
    ".cs": "csharp", ".m": "objc", ".mm": "objc",
    ".swift": "swift", ".dart": "dart", ".ex": "elixir", ".exs": "elixir",
    ".erl": "erlang", ".hs": "haskell", ".lua": "lua", ".r": "r", ".jl": "julia",
    ".zig": "zig", ".nim": "nim",
    ".vue": "vue", ".svelte": "svelte", ".astro": "astro",
    ".html": "html", ".htm": "html", ".css": "css", ".scss": "css", ".sass": "css", ".less": "css",
    ".tf": "terraform", ".tfvars": "terraform", ".hcl": "hcl",
    ".xml": "xml", ".gradle": "gradle", ".cmake": "cmake", ".mk": "make",
}

FILENAME_TO_LANG = {
    "Dockerfile": "dockerfile",
    "Makefile": "make",
    "Justfile": "make",
    "Rakefile": "ruby",
    "Procfile": "config",
    "CMakeLists.txt": "cmake",
}


def chunk_generic(text: str, file_path: str, lang: str) -> list[Chunk]:
    """Divide o arquivo em janelas de N linhas com sobreposição."""
    lines = text.splitlines()
    if not lines:
        return []
    window = settings.GENERIC_CHUNK_LINES
    overlap = settings.GENERIC_CHUNK_OVERLAP
    step = max(1, window - overlap)

    chunks: list[Chunk] = []
    start = 0
    while start < len(lines):
        end = min(start + window, len(lines))
        content = "\n".join(lines[start:end]).strip()
        if content:
            chunks.append(
                Chunk(
                    file_path=file_path,
                    lang=lang,
                    kind="block",
                    name=None,
                    start_line=start + 1,
                    end_line=end,
                    content=content,
                )
            )
        if end >= len(lines):
            break
        start += step
    return chunks
