---
description: Métricas del Kanban (WIP, throughput, work item age, cycle time) explicadas para la sustentación
---
1. Ejecuta `uv run scripts/tablero.py metricas` y muestra la tabla.
2. Ejecuta `gh pr list --state merged --limit 100 --json number --jq length` y
   `uv run python -c "import pathlib; print(len(list(pathlib.Path('specs').glob('*/spec.md'))))"`
   para contar PRs fusionadas y specs (meta: ≥ 40 y ≥ 40).
3. Explica en lenguaje sencillo, en 4 frases, qué dice cada métrica del proceso del
   proyecto hoy (por ejemplo: «el cycle time medio es X h; la historia más lenta fue Y
   porque…»). Así lo preguntará el profesor.
4. Señala riesgos: tarjetas con work item age alto, PRs abiertas sin revisión, días por
   debajo del ritmo del plan (`docs/plan-semana.md`).
