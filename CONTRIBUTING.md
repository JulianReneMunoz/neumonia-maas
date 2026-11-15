# Cómo contribuir a neumonia-maas

Esta guía es el reglamento del equipo en una página. No inventa reglas: resume lo que ya aplican
[`CLAUDE.md`](CLAUDE.md), los scripts del tablero y la
[plantilla de PR](.github/PULL_REQUEST_TEMPLATE.md), y enlaza a ellos para que haya una sola
fuente de verdad.

## Flujo de una historia

```
Backlog → spec → rama → PR → review → merge → Done
```

Cada historia `SPEC-NNN` es **1 issue = 1 tarjeta = 1 spec en `specs/NNN-slug/` = 1 PR**. La spec
(`spec.md`, `plan.md` y `tasks.md`) se commitea en la rama y se aprueba **antes** de escribir
código (desarrollo guiado por especificación, SDD).

| Paso | Comando (Claude Code) | Qué pasa | Tarjeta |
|---|---|---|---|
| 1. Elegir | `/siguiente` | Propone la historia con dependencias cumplidas y WIP libre. | Backlog |
| 2. Especificar | `/spec SPEC-NNN` (o `/lote` para varias) | Crea la rama `feature/NNN-slug` desde `develop` y escribe `spec.md`, `plan.md` y `tasks.md` (commit `docs(spec)`). Se detiene hasta que el usuario la aprueba. | Backlog |
| 3. Implementar | `/implementar SPEC-NNN` | Trae `develop` con merge, mueve la tarjeta y hace TDD tarea por tarea hasta `make check` en verde. | In Progress |
| 4. Abrir la PR | `/pr SPEC-NNN` | Push y PR hacia `develop` con la plantilla y `Closes #N`; el CI corre el check `ci`. | In Review |
| 5. Revisar | `/revisar <PR>` | El subagente `code-reviewer` revisa contra los AC y comenta en la PR (APROBAR o CAMBIOS). | In Review |
| 6. Fusionar | `/fusionar <PR>` | Solo con el check `ci` en verde y la revisión hecha: merge a `develop` y la rama se borra. | Done |

El número del issue es igual al de la spec (SPEC-001 = #1). Mover tarjetas a mano:
`uv run scripts/tablero.py mover SPEC-NNN "In Progress"`.

## Columnas y WIP limits

| Columna | WIP | Entra cuando… |
|---|---|---|
| Backlog | sin límite | La historia tiene Como/quiero/para, AC Given-When-Then y puntos Fibonacci. Aún no empieza. |
| In Progress | **1** (= nº de integrantes, una historia por persona) | Su spec está aprobada y empieza la implementación en su rama `feature/NNN-slug`. |
| In Review | **2** | La PR está abierta hacia `develop`, con la plantilla, `Closes #N` y el check `ci` corriendo. |
| Done | sin límite | La PR está fusionada con checks verdes, los AC se cumplen, la spec está `Implementada` y hay demo local. |

**Si una columna está llena, no se empieza otra historia**: primero se termina o se revisa lo que
está abierto. `uv run scripts/tablero.py mover` respeta estos límites. Las métricas (WIP,
throughput, work item age y cycle time) se ven con `uv run scripts/tablero.py metricas`.

## Definition of Done

Una historia está terminada solo si cumple las seis:

- [ ] Spec SDD aprobada (commiteada antes que el código)
- [ ] código
- [ ] pruebas (pytest, patrón AAA, sin red ni GPU)
- [ ] documentación (README, ADR o spec, según aplique)
- [ ] PR revisada y fusionada con checks verdes
- [ ] demo local del cambio

## Ramas (Gitflow)

- Cada historia vive en `feature/NNN-slug`, creada desde `develop`.
- Todo entra por PR: **nunca** commit, merge ni push directo a `main` o `develop`. La protección de
  ramas exige el check `ci` y que la rama esté al día con `develop`.
- Para traer cambios de `develop` se usa `git merge develop`, nunca rebase de una rama publicada.
- Prohibidos `--no-verify` y `push --force`.

## Commits (Conventional Commits)

Tipos: `feat`, `fix`, `test`, `docs`, `refactor`, `chore`. El ID de la spec va en el título o en
el cuerpo. Ejemplos:

```
docs(spec): SPEC-003 spec, plan y tareas
test: pruebas de las plantillas de issue (SPEC-003)
feat(ci): workflow de GitHub Actions con job ci (SPEC-002)
```

Si una spec aprobada cambia al implementar, el cambio va en su propio commit
`docs(spec): ajuste …` con la razón.

## Crear una historia y abrir la PR

- **Historia:** el backlog completo está en [`docs/backlog.yaml`](docs/backlog.yaml). Para una
  historia nueva, «New issue» → **Historia de usuario**. El formulario exige historia, AC,
  puntos Fibonacci (1, 2, 3, 5 u 8, una sola estimación) y la ruta de la spec `specs/NNN-slug/`.
  No hay issues en blanco.
- **Spec:** se escribe con las plantillas de [`docs/plantillas-sdd/`](docs/plantillas-sdd/).
- **PR:** usa la [plantilla de PR](.github/PULL_REQUEST_TEMPLATE.md), con `Closes #N`, el enlace a
  la spec, la salida real de las pruebas y la checklist de la Definition of Done.

## Reglas no negociables

Las revisa el profesor en vivo. El detalle completo está en [`CLAUDE.md`](CLAUDE.md).

- Nada de Streamlit, Gradio ni Dash: la UI es solo `frontend/` (React + TypeScript).
- Solo **uv** (Python 3.13): nunca `pip` ni `requirements.txt`; dependencias con `uv add`.
- Nada de notebooks: solo `.py` en `src/`, `scripts/` y `tests/`.
- Tres capas: `inference/` y `services/` no importan FastAPI; `api/` no tiene lógica de modelo.
- Pruebas pytest con patrón AAA, datos sintéticos, sin red ni GPU.
- Sin secretos ni datos de pacientes en el repo, en los logs ni en el navegador; los pesos del
  modelo nunca entran a Git.
