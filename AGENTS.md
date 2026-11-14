# AGENTS.md

Instrucciones para cualquier agente de código (Claude Code, Codex, Copilot, etc.).
La fuente completa es [`CLAUDE.md`](CLAUDE.md); este archivo es el resumen.

- **Proyecto:** servicio de clasificación de radiografías NORMAL/PNEUMONIA. React (frontend/)
  → FastAPI (src/neumonia/api) → servicio → modelo de Hugging Face fijado a una revisión.
- **Herramientas:** uv + Python 3.13 (nunca pip ni requirements.txt), pnpm para el frontend,
  gh para GitHub.
- **Prohibido:** Streamlit/Gradio/Dash, notebooks, pesos del modelo en Git, secretos,
  commits directos a `main`/`develop`, `--no-verify`, `push --force`.
- **SDD:** ninguna línea de código sin `specs/NNN-slug/{spec,plan,tasks}.md` commiteados
  y aprobados en la rama de la historia. Una spec ↔ una historia ↔ una PR.
- **Capas:** inference/ y services/ no importan FastAPI; api/ no tiene lógica de modelo.
- **Pruebas:** pytest AAA, sin red ni GPU, `FakeClassifier` para el modelo.
- **Verificar antes de terminar:** `uv run ruff check .` y `uv run pytest -q` en verde.
- **Idioma:** español.
