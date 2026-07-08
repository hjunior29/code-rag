"""Chunking estrutural via tree-sitter para Python, Go, TypeScript e JavaScript.

Extrai chunks no nível de símbolo (função/método/classe/struct/interface),
que é a granularidade que funciona melhor para busca semântica de código.
"""

import logging
from functools import lru_cache

from tree_sitter import Language, Node, Parser

from app.indexer.chunkers.base import Chunk

logger = logging.getLogger(__name__)


@lru_cache(maxsize=None)
def _get_parser(lang: str) -> Parser:
    if lang == "python":
        import tree_sitter_python as mod

        language = Language(mod.language())
    elif lang == "go":
        import tree_sitter_go as mod

        language = Language(mod.language())
    elif lang == "typescript":
        import tree_sitter_typescript as mod

        language = Language(mod.language_typescript())
    elif lang == "tsx":
        import tree_sitter_typescript as mod

        language = Language(mod.language_tsx())
    elif lang == "javascript":
        import tree_sitter_javascript as mod

        language = Language(mod.language())
    elif lang == "java":
        import tree_sitter_java as mod

        language = Language(mod.language())
    else:
        raise ValueError(f"linguagem sem gramática tree-sitter: {lang}")
    return Parser(language)


def _text(src: bytes, node: Node) -> str:
    return src[node.start_byte : node.end_byte].decode("utf-8", errors="replace")


def _mk(src: bytes, node: Node, file_path: str, lang: str, kind: str, name: str | None) -> Chunk:
    return Chunk(
        file_path=file_path,
        lang=lang,
        kind=kind,
        name=name,
        start_line=node.start_point[0] + 1,
        end_line=node.end_point[0] + 1,
        content=_text(src, node),
    )


def _child_by_type(node: Node, *types: str) -> Node | None:
    for child in node.children:
        if child.type in types:
            return child
    return None


def _field_name(src: bytes, node: Node) -> str | None:
    name_node = node.child_by_field_name("name")
    return _text(src, name_node) if name_node is not None else None


# ---------------------------------------------------------------- Python


def _chunk_python(src: bytes, root: Node, file_path: str) -> list[Chunk]:
    chunks: list[Chunk] = []

    def unwrap(node: Node) -> Node:
        if node.type == "decorated_definition":
            inner = _child_by_type(node, "function_definition", "class_definition")
            return inner if inner is not None else node
        return node

    for raw in root.children:
        node = unwrap(raw)
        if node.type == "function_definition":
            name = _field_name(src, node)
            chunks.append(_mk(src, raw, file_path, "python", "function", name))
        elif node.type == "class_definition":
            class_name = _field_name(src, node)
            chunks.append(_mk(src, raw, file_path, "python", "class", class_name))
            body = node.child_by_field_name("body")
            if body is None:
                continue
            for inner_raw in body.children:
                inner = unwrap(inner_raw)
                if inner.type != "function_definition":
                    continue
                method_name = _field_name(src, inner)
                qualified = f"{class_name}.{method_name}" if class_name and method_name else method_name
                chunks.append(_mk(src, inner_raw, file_path, "python", "method", qualified))
    return chunks


# ---------------------------------------------------------------- Go


def _chunk_go(src: bytes, root: Node, file_path: str) -> list[Chunk]:
    chunks: list[Chunk] = []
    for node in root.children:
        if node.type == "function_declaration":
            chunks.append(_mk(src, node, file_path, "go", "function", _field_name(src, node)))
        elif node.type == "method_declaration":
            name = _field_name(src, node)
            receiver = node.child_by_field_name("receiver")
            recv_type = None
            if receiver is not None:
                text = _text(src, receiver).strip("()")
                parts = text.split()
                if parts:
                    recv_type = parts[-1].lstrip("*")
            qualified = f"{recv_type}.{name}" if recv_type and name else name
            chunks.append(_mk(src, node, file_path, "go", "method", qualified))
        elif node.type == "type_declaration":
            for spec in node.children:
                if spec.type != "type_spec":
                    continue
                name = _field_name(src, spec)
                type_node = spec.child_by_field_name("type")
                kind = "type"
                if type_node is not None:
                    if type_node.type == "struct_type":
                        kind = "struct"
                    elif type_node.type == "interface_type":
                        kind = "interface"
                chunks.append(_mk(src, node, file_path, "go", kind, name))
    return chunks


# ---------------------------------------------------------------- Java

_JAVA_TYPE_KINDS = {
    "class_declaration": "class",
    "interface_declaration": "interface",
    "enum_declaration": "enum",
    "record_declaration": "class",
    "annotation_type_declaration": "interface",
}


def _chunk_java(src: bytes, root: Node, file_path: str) -> list[Chunk]:
    chunks: list[Chunk] = []

    def visit_type(node: Node, prefix: str) -> None:
        kind = _JAVA_TYPE_KINDS.get(node.type)
        if kind is None:
            return
        type_name = _field_name(src, node)
        qualified_type = f"{prefix}.{type_name}" if prefix and type_name else type_name
        chunks.append(_mk(src, node, file_path, "java", kind, qualified_type))
        body = node.child_by_field_name("body")
        if body is None:
            return
        for member in body.children:
            if member.type in ("method_declaration", "constructor_declaration"):
                method_name = _field_name(src, member)
                qualified = (
                    f"{qualified_type}.{method_name}" if qualified_type and method_name else method_name
                )
                chunks.append(_mk(src, member, file_path, "java", "method", qualified))
            elif member.type in _JAVA_TYPE_KINDS:
                # classes/interfaces aninhadas
                visit_type(member, qualified_type or "")

    for node in root.children:
        visit_type(node, "")
    return chunks


# ---------------------------------------------------------------- TS / JS


def _chunk_ts_js(src: bytes, root: Node, file_path: str, lang: str) -> list[Chunk]:
    chunks: list[Chunk] = []

    def visit_top(raw: Node) -> None:
        node = raw
        if node.type == "export_statement":
            inner = node.child_by_field_name("declaration")
            if inner is None:
                inner = _child_by_type(
                    node,
                    "function_declaration",
                    "class_declaration",
                    "lexical_declaration",
                    "interface_declaration",
                    "enum_declaration",
                    "type_alias_declaration",
                    "abstract_class_declaration",
                )
            if inner is None:
                return
            node = inner

        if node.type in ("function_declaration", "generator_function_declaration"):
            chunks.append(_mk(src, raw, file_path, lang, "function", _field_name(src, node)))
        elif node.type in ("class_declaration", "abstract_class_declaration"):
            class_name = _field_name(src, node)
            chunks.append(_mk(src, raw, file_path, lang, "class", class_name))
            body = node.child_by_field_name("body")
            if body is not None:
                for member in body.children:
                    if member.type != "method_definition":
                        continue
                    method_name = _field_name(src, member)
                    qualified = f"{class_name}.{method_name}" if class_name and method_name else method_name
                    chunks.append(_mk(src, member, file_path, lang, "method", qualified))
        elif node.type == "interface_declaration":
            chunks.append(_mk(src, raw, file_path, lang, "interface", _field_name(src, node)))
        elif node.type == "enum_declaration":
            chunks.append(_mk(src, raw, file_path, lang, "enum", _field_name(src, node)))
        elif node.type == "type_alias_declaration":
            chunks.append(_mk(src, raw, file_path, lang, "type", _field_name(src, node)))
        elif node.type == "lexical_declaration":
            # const foo = () => {...} / const foo = function() {...}
            for declarator in node.children:
                if declarator.type != "variable_declarator":
                    continue
                value = declarator.child_by_field_name("value")
                if value is None or value.type not in ("arrow_function", "function_expression", "function"):
                    continue
                chunks.append(_mk(src, raw, file_path, lang, "function", _field_name(src, declarator)))

    for raw in root.children:
        visit_top(raw)
    return chunks


# ---------------------------------------------------------------- dispatch

EXT_TO_TS_LANG = {
    ".py": "python",
    ".go": "go",
    ".java": "java",
    ".ts": "typescript",
    ".mts": "typescript",
    ".cts": "typescript",
    ".tsx": "tsx",
    ".js": "javascript",
    ".mjs": "javascript",
    ".cjs": "javascript",
    ".jsx": "javascript",
}


def chunk_with_treesitter(text: str, file_path: str, ts_lang: str) -> list[Chunk]:
    src = text.encode("utf-8")
    try:
        parser = _get_parser(ts_lang)
        tree = parser.parse(src)
    except Exception:
        logger.exception("falha no parse tree-sitter de %s", file_path)
        return []
    # tsx usa a mesma "linguagem lógica" typescript nos metadados
    lang = "typescript" if ts_lang == "tsx" else ts_lang
    if ts_lang == "python":
        return _chunk_python(src, tree.root_node, file_path)
    if ts_lang == "go":
        return _chunk_go(src, tree.root_node, file_path)
    if ts_lang == "java":
        return _chunk_java(src, tree.root_node, file_path)
    return _chunk_ts_js(src, tree.root_node, file_path, lang)
