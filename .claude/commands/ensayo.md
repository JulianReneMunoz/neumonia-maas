---
description: Prueba de 3 minutos antes de la sustentación (checklist del anuncio 007)
---
Corre cada paso, muestra el resultado y marca ✅/❌. No arregles nada sin preguntar.

1. `uv sync`
2. `uv run ruff check .`
3. `uv run pytest -q` → número de pruebas (meta ≥ 120)
4. `gh pr list --state merged --limit 100 --json number --jq length` → meta ≥ 40
5. Conteo de `specs/*/spec.md` → meta ≥ 40; abre dos al azar y confirma que tienen
   plan.md, tasks.md cerrado, issue y PR.
6. `git log --oneline --graph -20` → solo merges de PR en develop, sin commits directos.
7. Confirma que existen y están enlazados desde el README: `docs/model-card.md`,
   `docs/arquitectura.html`, `LICENSE`, enlace al tablero y a `specs/`.
8. Recuérdale al usuario levantar, cada uno en su terminal: `make mlflow`, `make backend`,
   `make frontend`; y tener abiertos: la app, la pestaña Network, /docs, el tablero,
   MLflow (comparación de 3 runs), el IDE y una spec.
9. Resume lo que falla, ordenado por peso en la rúbrica (Demo 25 %, MLflow 20 %,
   Kanban 15 %, Backend 15 %, QA y Git 15 %, Model Card 10 %).
