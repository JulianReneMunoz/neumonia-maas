# CLAUDE.md — neumonia-maas

Guía para Claude Code en este repositorio. Léela completa antes de cualquier tarea.

## Qué es el proyecto
Servicio de apoyo a la lectura de radiografías de tórax (curso GPIA, UAO 2026-2S, Módulo 3).
Un **frontend desacoplado (React + TypeScript, Vite)** envía la imagen por HTTP a una
**API FastAPI**, que la pasa a una **capa de servicio**, que usa un **modelo preentrenado
de Hugging Face Hub** (`lxyuan/vit-xray-pneumonia-classification`, Apache-2.0,
fijado a una revisión). MLflow registra las evaluaciones.

```
Navegador → React (frontend/) → HTTP/JSON → FastAPI (src/neumonia/api) →
DiagnosisService (src/neumonia/services) → Classifier (src/neumonia/inference) → ViT de HF
```

El backlog completo está en `docs/backlog.yaml`. Cada historia `SPEC-NNN` (= issue = tarjeta) tiene exactamente
una carpeta `specs/NNN-slug/` y se implementa en exactamente una PR.

## Reglas que no se negocian (las revisa el profesor en vivo)
1. **Nada de Streamlit, Gradio ni Dash.** La UI es solo `frontend/`.
2. **Solo uv** (Python 3.13). Nunca `pip`, nunca `requirements.txt`. Dependencias con `uv add`.
3. **Nada de notebooks** (.ipynb). Solo `.py` en `src/`, `scripts/` y `tests/`.
4. **Spec antes que código (SDD).** No escribas código de una historia si su `spec.md`,
   `plan.md` y `tasks.md` no están commiteados en la rama y aprobados por el usuario.
5. **Gitflow.** Ramas `feature/NNN-slug` desde `develop`. Nunca commit, merge ni push
   directo a `main` o `develop`; todo entra por PR. Nunca `--no-verify` ni `push --force`.
6. **Conventional Commits** (`feat:`, `fix:`, `test:`, `docs:`, `refactor:`, `chore:`),
   con el ID de la spec en el cuerpo o el título.
7. **Tres capas.** `inference/` no importa FastAPI. `services/` no importa FastAPI ni
   recibe `Request`. `api/` no tiene lógica de modelo.
8. **El modelo se carga una sola vez** (lifespan) y los **pesos nunca entran a Git**.
9. **Pruebas pytest con patrón AAA**, datos sintéticos, sin red y sin GPU. torch y
   transformers se importan de forma perezosa; las pruebas usan `FakeClassifier`.
10. **Sin secretos ni datos de pacientes** en el repo, en los logs ni en el navegador.

## Comandos
| Para | Comando |
|---|---|
| Instalar | `uv sync` |
| Calidad completa | `make check` (ruff + pytest) |
| Backend | `make backend` → http://127.0.0.1:8000/docs |
| Frontend | `make frontend` → http://localhost:5173 |
| MLflow | `make mlflow` → http://127.0.0.1:5050 |
| Tablero | `uv run scripts/tablero.py metricas` |

(Hasta que SPEC-001 cree el Makefile, usa `uv run ruff check .` y `uv run pytest -q`.)

## Flujo SDD de cada historia (comandos de este repo)
1. `/siguiente` — qué historia toca (dependencias cumplidas, WIP libre).
1b. `/lote SPEC-a SPEC-b …` — (modo rápido) escribe varias specs seguidas, sin código, para aprobarlas de una vez.
2. `/spec SPEC-NNN` — rama + spec.md/plan.md/tasks.md + commit `docs(spec)` → **se detiene**
   para que el usuario la lea y apruebe.
3. `/implementar SPEC-NNN` — TDD tarea por tarea, marca `tasks.md`, `make check` en verde.
4. `/pr SPEC-NNN` — push, PR con plantilla y `Closes #N`, tarjeta a *In Review*.
5. `/revisar <PR>` — el subagente `code-reviewer` revisa contra los AC y comenta en la PR.
6. `/fusionar <PR>` — solo con checks verdes y revisión; merge a develop, tarjeta a *Done*.

## Definition of Done (las seis)
Spec SDD aprobada · código · pruebas · documentación · PR revisada y fusionada con checks
verdes · demo local del cambio.

## Ubicación
El proyecto vive en `C:\Neumonia` (repo **nuevo**). El proyecto anterior (Streamlit) quedó en `C:\Neumonia_viejo`: no copies código ni specs de ahí, no uses su historial. Los datos de RSNA están en `data/raw/rsna/` y `data/raw/rsna_csv/` (ignorados por Git).

## Plazo
Sustentación del M3: **jueves 19/11/2026**; todo listo el **miércoles 18**. Plan en `docs/plan-semana.md`. Prioridad si aprieta: demo E2E (25 %) y MLflow (20 %) antes que volumen.

## Cómo trabajar con el usuario
- Escribe y responde en **español**.
- El usuario debe **poder explicar cada línea** en la sustentación. Al cerrar cada
  `/implementar`, explícale en 5 viñetas qué hiciste y por qué, y hazle **una pregunta**
  de comprobación sobre una decisión de la historia.
- Si un criterio de aceptación no se puede cumplir tal como está, **detente y pregunta**;
  no cambies la spec sin permiso. Si cambia, va en un commit `docs(spec): ajuste …` con
  la razón.
- No inventes métricas: los números de la Model Card y del README salen de MLflow.
- El usuario trabaja en **Windows** (PowerShell + Git Bash). Prefiere comandos que
  funcionen en ambos; los scripts van en Python, no en bash.

## Estructura objetivo
```
src/neumonia/{config.py, inference/, services/, api/, tracking/}
frontend/                React + TS + Vite (pnpm)
scripts/                 descargar_modelo.py, preparar_eval.py, evaluar.py, tablero.py
configs/                 baseline.yaml, umbral-035.yaml, clahe.yaml
specs/NNN-slug/          spec.md, plan.md, tasks.md
docs/                    backlog.yaml, model-card.md, arquitectura.html, adr/, openapi.json
tests/                   unit/, integration/, conftest.py
```
