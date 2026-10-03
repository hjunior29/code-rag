"""Entrypoint multi-modo:

  python -m app.main serve                       # servidor HTTP (UI + API + MCP em /mcp)
  python -m app.main index --path DIR --name X   # indexa uma pasta de código
  python -m app.main mcp                         # servidor MCP via stdio
"""

import argparse
import asyncio
import json
import logging
import sys

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
# Bibliotecas barulhentas: só warnings/erros
for noisy in ("httpx", "httpcore", "huggingface_hub", "urllib3", "filelock"):
    logging.getLogger(noisy).setLevel(logging.WARNING)


def main() -> None:
    parser = argparse.ArgumentParser(prog="code-rag")
    sub = parser.add_subparsers(dest="mode", required=True)

    sub.add_parser("serve", help="servidor HTTP (UI + API + MCP)")

    p_index = sub.add_parser("index", help="indexa uma pasta de código")
    p_index.add_argument("--path", required=True, help="caminho da pasta a indexar")
    p_index.add_argument("--name", required=True, help="nome do projeto no índice")
    p_index.add_argument(
        "--display-path",
        default=None,
        help="caminho exibido nas listagens (ex.: caminho do host quando --path é um mount)",
    )

    sub.add_parser("mcp", help="servidor MCP via stdio")

    args = parser.parse_args()

    if args.mode == "serve":
        import uvicorn

        from app.config import settings

        uvicorn.run("app.web.api:app", host="0.0.0.0", port=settings.HTTP_PORT, log_level="info")
    elif args.mode == "index":
        from app.indexer.pipeline import index_path

        summary = asyncio.run(index_path(args.path, args.name, display_path=args.display_path))
        print(json.dumps(summary, ensure_ascii=False))
    elif args.mode == "mcp":
        from app.mcp_server import mcp

        mcp.run("stdio")
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
