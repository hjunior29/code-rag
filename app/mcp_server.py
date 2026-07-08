"""Servidor MCP (FastMCP) com as ferramentas de consulta ao code-rag.

Exposto de duas formas:
  - HTTP (streamable) montado em /mcp pelo servidor web
  - stdio via `python -m app.main mcp`
"""

from mcp.server.fastmcp import FastMCP

from app import search

mcp = FastMCP("code-rag", stateless_http=True, streamable_http_path="/")


@mcp.tool()
async def search_code(
    query: str,
    project: str | None = None,
    lang: str | None = None,
    top_k: int = 10,
) -> list[dict]:
    """Busca semântica por código nos projetos indexados.

    Args:
        query: pergunta em linguagem natural ou descrição do código procurado.
        project: (opcional) restringe a um projeto indexado — veja list_projects.
        lang: (opcional) filtra por linguagem: python, go, typescript, javascript, etc.
        top_k: quantidade de resultados (1-50, padrão 10).
    """
    return await search.search_code(query=query, project=project, lang=lang, top_k=top_k)


@mcp.tool()
async def find_symbol(symbol: str, project: str | None = None, top_k: int = 20) -> list[dict]:
    """Localiza um símbolo (função, classe, método, struct...) pelo nome, com match exato ou parcial.

    Args:
        symbol: nome do símbolo, ex. 'UserService' ou 'parse_config'.
        project: (opcional) restringe a um projeto indexado.
        top_k: quantidade de resultados (1-100, padrão 20).
    """
    return await search.find_symbol(symbol=symbol, project=project, top_k=top_k)


@mcp.tool()
async def list_projects() -> list[dict]:
    """Lista os projetos indexados no code-rag, com contagem de arquivos/chunks e data da indexação."""
    return await search.list_projects()
