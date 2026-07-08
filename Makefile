# ===== code-rag =====
# make up                          -> sobe toda a infra (postgres + ollama + servidor)
# make index DIR=/caminho/projeto  -> indexa qualquer pasta de código
# make down / logs / ps / reset-db

-include .env

NAME ?= $(notdir $(patsubst %/,%,$(DIR)))

.PHONY: setup up down restart logs ps index reset-db mcp-stdio help

help:
	@echo "code-rag — RAG local e agnóstico de base de código"
	@echo ""
	@echo "  make up                            sobe toda a infra (docker)"
	@echo "  make index DIR=/caminho [NAME=x]   indexa uma pasta de código"
	@echo "  make down                          derruba a infra"
	@echo "  make logs                          logs do servidor"
	@echo "  make ps                            status dos containers"
	@echo "  make reset-db                      APAGA o banco (necessário ao trocar de modelo)"
	@echo ""
	@echo "  UI:  http://localhost:8000    MCP: http://localhost:8000/mcp"

setup:
	@test -f .env || (cp .env.example .env && echo "✓ .env criado a partir de .env.example")

up: setup
	docker compose up -d --build
ifeq ($(EMBEDDING_PROVIDER),ollama)
ifneq ($(findstring ollama,$(COMPOSE_PROFILES)),)
	@echo "→ garantindo modelo de embedding '$(EMBEDDING_MODEL)' no Ollama..."
	docker compose exec ollama ollama pull $(EMBEDDING_MODEL)
endif
endif
	@echo ""
	@echo "✓ code-rag no ar:"
	@echo "    UI:   http://localhost:8000"
	@echo "    MCP:  http://localhost:8000/mcp"
	@echo ""
	@echo "  Próximo passo: make index DIR=/caminho/da/sua/base-de-codigo"

down:
	docker compose down

restart:
	docker compose restart server

logs:
	docker compose logs -f server

ps:
	docker compose ps

index:
ifndef DIR
	$(error Uso: make index DIR=/caminho/absoluto/do/projeto [NAME=nome-no-indice])
endif
	docker compose run --rm --no-deps \
		-v "$(abspath $(DIR)):/workspace:ro" \
		server python -m app.main index --path /workspace --name "$(NAME)" \
		--display-path "$(abspath $(DIR))"

reset-db:
	docker compose down
	docker volume rm -f $$(basename $$PWD)_pgdata
	@echo "✓ banco apagado. Rode 'make up' e reindexe seus projetos."

# Servidor MCP via stdio (alternativa ao HTTP), para clientes que preferem stdio
mcp-stdio:
	docker compose run --rm -T --no-deps server python -m app.main mcp
