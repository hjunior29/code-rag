"""Servidor HTTP: UI de busca, API JSON e MCP montado em /mcp."""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Query
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from app import db, search
from app.mcp_server import mcp

_STATIC = Path(__file__).parent / "static"

# Precisa existir antes do lifespan para o session_manager estar disponível
mcp_app = mcp.streamable_http_app()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await db.ensure_base_schema()
    async with mcp.session_manager.run():
        yield
    await db.close_pool()


app = FastAPI(title="code-rag", lifespan=lifespan)
app.mount("/mcp", mcp_app)
app.mount("/assets", StaticFiles(directory=_STATIC / "assets"), name="assets")


@app.get("/health")
async def health() -> dict:
    pool = await db.get_pool()
    await pool.fetchval("SELECT 1")
    return {"status": "ok"}


@app.get("/api/search")
async def api_search(
    q: str = Query(..., min_length=1),
    project: str | None = None,
    lang: str | None = None,
    top_k: int = 10,
) -> list[dict]:
    return await search.search_code(query=q, project=project, lang=lang, top_k=top_k)


@app.get("/api/projects")
async def api_projects() -> list[dict]:
    return await search.list_projects()


@app.get("/api/langs")
async def api_langs() -> list[str]:
    return await search.list_langs()


@app.get("/")
async def index() -> FileResponse:
    return FileResponse(_STATIC / "index.html")


@app.get("/search")
async def search_page() -> FileResponse:
    return FileResponse(_STATIC / "search.html")


@app.get("/how")
async def how_it_works() -> RedirectResponse:
    return RedirectResponse(url="/", status_code=307)
