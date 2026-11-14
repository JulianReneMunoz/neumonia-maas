## Historia y spec
- Cierra: Closes #
- Spec SDD: [`specs/NNN-slug/spec.md`](../specs/NNN-slug/spec.md) (SPEC-NNN)

## ¿Qué cambia?
<!-- Una funcionalidad o corrección por PR. Qué se agregó/modificó, en 2-4 líneas. -->

## ¿Por qué?
<!-- Qué historia/AC resuelve y qué decisión del plan.md se implementó. -->

## ¿Cómo se probó?
<!-- Pega la salida real: `uv run pytest -q` y, si aplica, curl / captura / comando de la demo. -->
```
```

## Criterios de aceptación
- [ ] AC-1:
- [ ] AC-2:
- [ ] AC-3:

## Riesgos y fuera de alcance
<!-- Qué podría romperse y qué quedó fuera a propósito. -->

## Checklist (Definition of Done)
- [ ] La spec (spec.md, plan.md, tasks.md) se commiteó **antes** que el código
- [ ] Todas las tareas de `tasks.md` están marcadas `[x]`
- [ ] Pruebas nuevas (AAA, sin red ni GPU) y `uv run pytest -q` en verde
- [ ] `uv run ruff check .` y `uv run ruff format --check .` en verde
- [ ] Capas respetadas (inference/ y services/ sin FastAPI; api/ sin lógica de modelo)
- [ ] Sin pip, notebooks, Streamlit, pesos ni secretos
- [ ] Documentación actualizada (README/ADR/spec) si aplica
- [ ] Título en Conventional Commits con el ID de la spec
