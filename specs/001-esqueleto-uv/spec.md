# SPEC-001 · Esqueleto del proyecto con uv y Python 3.13

- **Estado:** Implementada <!-- Borrador → Aprobada → Implementada -->
- **Historia:** #1 · **Puntos:** 2 · **Milestone:** M3 · **Labels:** infra
- **Depende de:** ninguna
- **PR:** #N (se completa al abrirla)

## 1. Problema y contexto
Hoy el repositorio solo tiene el kit inicial (backlog, plantillas, scripts del tablero): no
hay paquete Python, ni `pyproject.toml`, ni `uv.lock`, ni pruebas, ni linter configurado.
Sin este esqueleto ninguna otra historia (configuración, clasificador, API, MLflow, CI)
puede empezar, porque todas dependen de un paquete instalable con `uv sync` y de una
compuerta de calidad (`ruff` + `pytest`) que se pueda repetir igual en cualquier máquina.
Para la rúbrica importa porque el profesor revisa en vivo que se use **solo uv** (nada de
`pip` ni `requirements.txt`), que el proyecto se instale en una máquina limpia y que haya
pruebas automatizadas desde el primer día.

## 2. Historia
**Como** desarrollador del proyecto, **quiero** un proyecto uv con Python 3.13, ruff y
pytest listos **para** que cualquiera lo instale con `uv sync` en una máquina limpia.

## 3. Requisitos
### Funcionales
- RF-1: Existe un paquete importable `neumonia` con layout `src/neumonia/` y una carpeta
  `tests/` (con `tests/unit/`, `tests/integration/` y `tests/conftest.py`).
- RF-2: `pyproject.toml` declara el proyecto `neumonia`, `requires-python = ">=3.13"` y
  `build-backend = "uv_build"`.
- RF-3: `.python-version` contiene `3.13`.
- RF-4: El grupo de dependencias `dev` contiene `pytest`, `pytest-cov` y `ruff`, añadidos
  con `uv add --dev`; `uv.lock` se versiona en Git.
- RF-5: `neumonia.__version__` expone la versión del paquete (cadena tipo `X.Y.Z`) y
  coincide con la declarada en `pyproject.toml`.
- RF-6: ruff está configurado en `pyproject.toml` con las reglas `E`, `F`, `I`, `UP`, `B`,
  `D` (convención `google`) y `ANN`, y `target-version = "py313"`.
- RF-7: pytest está configurado en `pyproject.toml` con `testpaths = ["tests"]`, `-q` en
  `addopts` y `filterwarnings = ["error"]`.
- RF-8: Existe un `Makefile` con, al menos, los objetivos `install`, `lint`, `format`,
  `test` y `check`; `check` ejecuta ruff (check + format --check) y pytest, todo vía `uv run`.

### No funcionales
- RNF-1: Solo uv. No existe ningún `requirements*.txt` ni instrucciones con `pip`.
- RNF-2: Sin notebooks (`.ipynb`) en el repositorio.
- RNF-3: Las pruebas no usan red ni GPU y siguen el patrón AAA; la suite completa corre
  en menos de 5 s.
- RNF-4: Los scripts existentes del kit (`scripts/*.py`, `.claude/hooks/guardia.py`)
  siguen funcionando con `uv run scripts/<x>.py` (sus metadatos PEP 723 no se tocan).
- RNF-5: Los comandos funcionan igual en Windows (PowerShell y Git Bash) y Linux; las
  recetas del Makefile solo invocan `uv run …` (sin utilidades de shell POSIX).

## 4. Criterios de aceptación (Given-When-Then)
**AC-1** (backlog)
- **Dado** un clon limpio del repositorio
- **Cuando** ejecuto `uv sync` y `uv run pytest -q`
- **Entonces** se instalan las dependencias desde `uv.lock` y las pruebas pasan

**AC-2** (backlog)
- **Dado** el proyecto recién instalado
- **Cuando** ejecuto `uv run ruff check .` y `uv run ruff format --check .`
- **Entonces** no hay errores

**AC-3** (backlog)
- **Dado** el Makefile
- **Cuando** ejecuto `make check`
- **Entonces** corre ruff + pytest y termina en verde

**AC-4** (añadido: versión del paquete)
- **Dado** el paquete instalado con `uv sync`
- **Cuando** ejecuto `uv run python -c "import neumonia; print(neumonia.__version__)"`
- **Entonces** imprime una versión `X.Y.Z` igual a `project.version` de `pyproject.toml`

**AC-5** (añadido: lock coherente)
- **Dado** el `pyproject.toml` y el `uv.lock` commiteados
- **Cuando** ejecuto `uv sync --locked`
- **Entonces** termina sin error (el lock está al día con el pyproject; base para SPEC-002)

**AC-6** (añadido: reglas de la rúbrica)
- **Dado** el repositorio
- **Cuando** busco `requirements*.txt` o archivos `.ipynb` versionados
- **Entonces** no existe ninguno y la prueba correspondiente lo verifica

**AC-7** (añadido: advertencias como error)
- **Dado** `filterwarnings = ["error"]` en la configuración de pytest
- **Cuando** una prueba emite una advertencia no filtrada
- **Entonces** la prueba falla (se verifica leyendo la configuración, no provocando la advertencia)

**AC-8** (añadido: archivos existentes del kit)
- **Dado** los scripts existentes `scripts/auditar_rubrica.py`, `bootstrap_github.py`,
  `completar_tablero.py`, `ghlib.py`, `tablero.py` y `.claude/hooks/guardia.py`
- **Cuando** ejecuto `uv run ruff check .` y `uv run ruff format --check .`
- **Entonces** pasan sin excluirlos de ruff (como máximo un `# noqa` en línea y comentado)
  y `uv run scripts/tablero.py --help` sigue funcionando igual que antes

## 5. Fuera de alcance
- Workflow de GitHub Actions (SPEC-002) y pre-commit (SPEC-036).
- Configuración tipada con pydantic-settings (SPEC-004) y cualquier dependencia de
  runtime (FastAPI, torch, transformers, MLflow…): `dependencies` queda vacío.
- Objetivos `backend`, `frontend` y `mlflow` del Makefile (los añade cada historia que
  crea ese componente).
- README definitivo con badges (SPEC-037); aquí solo no se rompe el README actual.
- Umbral mínimo de cobertura (`--cov-fail-under`): pytest-cov se instala pero no se exige.

## 6. Métricas de éxito
- `uv sync` + `uv run pytest -q` en verde en un clon limpio en menos de 1 minuto (con caché de uv).
- `make check` en verde con 0 errores de ruff y ≥ 3 pruebas pasando (plan: 9).
- 0 archivos `requirements*.txt` y 0 `.ipynb` en el repo.

## 7. Preguntas abiertas
Resueltas en la aprobación (14/11/2026):
1. **`make` en Windows.** El usuario tiene `make` en Windows. Se documentan además los
   equivalentes `uv run` en el README (T11); no se crea `scripts/check.py`.
2. **Scripts del kit y ruff.** Aceptado: se corrigen en esta PR (cambios mecánicos, AC-8).
3. **Docstrings en pruebas.** Aceptado: `D100`–`D104` desactivados solo en `tests/**`.
4. **Número del issue:** #1 (el número del issue es igual al de la spec).
