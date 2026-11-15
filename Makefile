# Atajos del proyecto. Cada receta solo llama a `uv run …`, así funciona igual en
# Git Bash, PowerShell (con make instalado) y Linux/CI. Sin make: copia el comando.

.PHONY: install lint format test check

install: ## Instala dependencias exactas desde uv.lock
	uv sync

lint: ## Estilo, imports, anotaciones y docstrings (no modifica archivos)
	uv run ruff check .
	uv run ruff format --check .

format: ## Formatea y aplica correcciones automáticas
	uv run ruff format .
	uv run ruff check --fix .

test: ## Pruebas pytest (advertencias = error)
	uv run pytest

check: lint test ## Compuerta de calidad: ruff + pytest
