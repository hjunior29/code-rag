"""Modelo de chunk compartilhado pelos chunkers."""

from dataclasses import dataclass


@dataclass
class Chunk:
    file_path: str  # relativo à raiz do projeto
    lang: str
    kind: str  # function | method | class | struct | interface | type | block | ...
    name: str | None  # nome qualificado quando possível (ex.: MinhaClasse.metodo)
    start_line: int  # 1-indexado
    end_line: int
    content: str
