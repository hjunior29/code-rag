"""Caminha uma árvore de arquivos ignorando diretórios de build/deps e binários."""

import logging
import os
from pathlib import Path

from app.config import settings

logger = logging.getLogger(__name__)

IGNORE_DIRS = {
    ".git",
    ".hg",
    ".svn",
    "node_modules",
    "vendor",
    "__pycache__",
    ".venv",
    "venv",
    "env",
    "dist",
    "build",
    "out",
    ".next",
    ".nuxt",
    ".output",
    "target",
    ".idea",
    ".vscode",
    "coverage",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".terraform",
    ".gradle",
    ".dart_tool",
    "Pods",
    ".turbo",
    ".cache",
}

IGNORE_FILES = {
    "package-lock.json",
    "yarn.lock",
    "pnpm-lock.yaml",
    "poetry.lock",
    "uv.lock",
    "Cargo.lock",
    "composer.lock",
    "Gemfile.lock",
    "go.sum",
}

# Extensões tratadas como texto indexável (as com tree-sitter + genéricas)
TEXT_EXTENSIONS = {
    # tree-sitter
    ".py", ".go", ".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs",
    # genéricas (chunker por janela de linhas)
    ".md", ".mdx", ".txt", ".rst",
    ".json", ".yaml", ".yml", ".toml", ".ini", ".cfg", ".conf", ".env.example",
    ".sql", ".graphql", ".proto", ".prisma",
    ".sh", ".bash", ".zsh", ".fish", ".ps1",
    ".rb", ".rs", ".java", ".kt", ".kts", ".scala", ".php",
    ".c", ".h", ".cpp", ".hpp", ".cc", ".hh", ".cs", ".m", ".mm",
    ".swift", ".dart", ".ex", ".exs", ".erl", ".hs", ".lua", ".r", ".jl", ".zig", ".nim",
    ".vue", ".svelte", ".astro", ".html", ".htm", ".css", ".scss", ".sass", ".less",
    ".tf", ".tfvars", ".hcl", ".dockerfile", ".xml", ".gradle", ".cmake", ".mk",
}

# Arquivos sem extensão que valem indexar
TEXT_FILENAMES = {"Dockerfile", "Makefile", "Rakefile", "Procfile", "Justfile", "CMakeLists.txt"}


def walk_files(root: Path) -> list[Path]:
    """Retorna arquivos de texto indexáveis sob root."""
    max_bytes = settings.MAX_FILE_SIZE_KB * 1024
    files: list[Path] = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS and not d.startswith(".")]
        for fname in filenames:
            if fname in IGNORE_FILES:
                continue
            path = Path(dirpath) / fname
            ext = path.suffix.lower()
            if ext not in TEXT_EXTENSIONS and fname not in TEXT_FILENAMES:
                continue
            try:
                if path.stat().st_size > max_bytes:
                    logger.debug("pulando arquivo grande: %s", path)
                    continue
            except OSError:
                continue
            files.append(path)
    return sorted(files)


def read_text(path: Path) -> str | None:
    """Lê o arquivo como UTF-8; retorna None se for binário/ilegível."""
    try:
        raw = path.read_bytes()
    except OSError:
        return None
    if b"\x00" in raw[:8192]:
        return None
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        try:
            return raw.decode("latin-1")
        except UnicodeDecodeError:
            return None
