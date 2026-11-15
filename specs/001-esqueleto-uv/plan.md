# Plan · SPEC-001

## 1. Diseño técnico
| Archivo | Cambio |
|---|---|
| `pyproject.toml` | **Crear.** Metadatos del proyecto `neumonia` (`version = "0.1.0"`, `requires-python = ">=3.13"`, `dependencies = []`), `[build-system]` con `uv_build`, `[dependency-groups] dev`, `[tool.ruff]`, `[tool.ruff.lint]`, `[tool.pytest.ini_options]`. |
| `.python-version` | **Crear.** Una línea: `3.13`. |
| `uv.lock` | **Crear** (lo genera uv, se versiona). |
| `src/neumonia/__init__.py` | **Crear.** Docstring del paquete y `__version__`. |
| `tests/__init__.py` | No se crea (pytest en modo `importlib`/rootdir; ver decisiones). |
| `tests/conftest.py` | **Crear.** Fixture `raiz_repo() -> Path` (raíz del repo) y `pyproject() -> dict[str, Any]` (pyproject parseado con `tomllib`). |
| `tests/unit/test_paquete.py` | **Crear.** Pruebas de versión del paquete. |
| `tests/unit/test_proyecto.py` | **Crear.** Pruebas de configuración (pyproject, `.python-version`, Makefile, reglas de la rúbrica). |
| `tests/integration/.gitkeep` | **Crear** (carpeta reservada para SPEC de API). |
| `Makefile` | **Crear.** Objetivos `install`, `lint`, `format`, `test`, `check` (y `.PHONY`). |
| `scripts/auditar_rubrica.py` | **Modificar** (mecánico): `ruff format` (hoy sin formato). Lint ya limpio. |
| `scripts/bootstrap_github.py` | **Modificar** (mecánico): `ruff format` + cortar 4 líneas > 100 (E501). |
| `scripts/completar_tablero.py` | **Modificar** (mecánico): `ruff format` + 3 E501 + docstring de módulo como `r"""` (D301). |
| `scripts/ghlib.py` | **Modificar** (mínimo): 1 E501 y `gh_json(...) -> Any` con `# noqa: ANN401` comentado (la salida de `gh --json` es JSON arbitrario: lista, dict o `None`). Formato ya correcto. |
| `scripts/tablero.py` | **Modificar** (mecánico): `ruff format` + quitar sangría extra del docstring de uso (5 × D208) + 3 E501. |
| `.claude/hooks/guardia.py` | **Sin cambios esperados:** hoy pasa lint y formato con la configuración nueva; T8 lo verifica. |
| `scripts/__pycache__/` | Ignorado (ya está en `.gitignore`; ruff no analiza `.pyc`). |
| `README.md` | **Modificar** mínimamente: sección «Instalación y calidad» con `uv sync`, `make check` y los equivalentes `uv run` para quien no tenga `make`. |

### Firmas públicas
```python
# src/neumonia/__init__.py
__version__: str  # = importlib.metadata.version("neumonia")
```
```python
# tests/conftest.py
@pytest.fixture
def raiz_repo() -> Path: ...
@pytest.fixture
def pyproject(raiz_repo: Path) -> dict[str, Any]: ...
```

### Cómo se genera (solo uv)
1. `uv init --lib --name neumonia --python 3.13 --build-backend uv .` en la raíz (crea
   `pyproject.toml`, `.python-version`, `src/neumonia/__init__.py`, `py.typed`).
   Verificar con `git diff` que no tocó `README.md` ni `.gitignore`.
2. `uv add --dev pytest pytest-cov ruff` (crea `uv.lock`).
3. Editar a mano las secciones `[tool.ruff*]` y `[tool.pytest.ini_options]`.

## 2. Contratos
**`pyproject.toml` (extracto del contrato que verifican las pruebas):**
```toml
[project]
name = "neumonia"
version = "0.1.0"
requires-python = ">=3.13"
dependencies = []

[build-system]
requires = ["uv_build>=0.13,<0.14"]
build-backend = "uv_build"

[dependency-groups]
dev = ["pytest>=…", "pytest-cov>=…", "ruff>=…"]   # versiones las fija uv add

[tool.ruff]
line-length = 100
target-version = "py313"

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B", "D", "ANN"]

[tool.ruff.lint.pydocstyle]
convention = "google"

[tool.ruff.lint.per-file-ignores]
"tests/**" = ["D100", "D101", "D102", "D103", "D104"]

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = ["-q", "--import-mode=importlib"]
filterwarnings = ["error"]
```

**`Makefile` (contrato de objetivos):**
| Objetivo | Receta |
|---|---|
| `install` | `uv sync` |
| `lint` | `uv run ruff check .` y `uv run ruff format --check .` |
| `format` | `uv run ruff format .` y `uv run ruff check --fix .` |
| `test` | `uv run pytest` |
| `check` | depende de `lint` y `test` |

**`neumonia.__version__`:** `str` con formato `^\d+\.\d+\.\d+` igual a `project.version`.

## 3. Decisiones de diseño
| Decisión | Alternativas descartadas | Por qué |
|---|---|---|
| `__version__` se lee con `importlib.metadata.version("neumonia")` | Cadena literal duplicada en `__init__.py` | Una sola fuente de verdad (`pyproject.toml`); `uv sync` siempre instala el paquete en modo editable, así que la metadata existe. |
| Build backend `uv_build` con layout `src/` | hatchling, setuptools; layout plano | Lo piden las notas del backlog; `uv_build` es nativo de uv y el layout `src/` evita importar el paquete sin instalarlo. |
| Configuración de ruff y pytest dentro de `pyproject.toml` | `ruff.toml`, `pytest.ini` separados | Un solo archivo que revisar en la sustentación. |
| `line-length = 100` | 88 (default) | Docstrings y mensajes en español son más largos; con 100 los scripts existentes solo requieren 11 cortes. |
| Ignorar `D100`–`D104` en `tests/**` | Exigir docstring en cada prueba | El nombre `test_…` en español ya documenta el caso; se mantiene `ANN` (las pruebas llevan `-> None`). |
| `--import-mode=importlib` y sin `tests/__init__.py` | `tests/__init__.py` + modo `prepend` | Recomendado por pytest para layout `src/`; evita colisiones de nombres entre `unit/` e `integration/`. |
| Pruebas de configuración leen archivos (`tomllib`, texto del Makefile), no lanzan `ruff`/`make` en subprocesos | Ejecutar `ruff`/`make` desde pytest | Rápidas, sin depender de `make` en Windows y sin recursión (`make check` → pytest → make). AC-2 y AC-3 se verifican además ejecutando los comandos en la demo y luego en CI (SPEC-002). |
| **Archivos existentes:** `uv run ruff check .` y `ruff format --check .` analizan también `scripts/*.py` y `.claude/hooks/guardia.py` (ruff no excluye `.claude/` por defecto). Se **corrigen** en esta PR (18 hallazgos medidos: 11 E501, 5 D208, 1 D301, 1 ANN401; 4 archivos sin formato) en vez de excluirlos. Única excepción: un `# noqa: ANN401` en línea, con comentario, en `ghlib.gh_json`. | `extend-exclude = ["scripts", ".claude"]`; `per-file-ignores` amplios para `scripts/**` (E501, D, ANN) | Los scripts futuros del curso (`descargar_modelo.py`, `evaluar.py`, `preparar_eval.py`) vivirán en `scripts/` y deben pasar la misma compuerta; excluir la carpeta o relajar reglas por patrón los dejaría sin revisar. Las correcciones son de formato, sin cambio de comportamiento, y el `noqa` acotado a una línea documenta el único caso legítimo de `Any`. |
| Recetas del Makefile solo con `uv run …` | Recetas con `rm`, `find`, `&&` POSIX | Funcionan igual desde Git Bash, PowerShell (si hay make) y Linux/CI. |

## 4. Riesgos
- **`make` no instalado en Windows/PowerShell.** Mitigación: recetas triviales con
  equivalentes `uv run` documentados en el README; Git Bash de esta máquina ya trae
  GNU Make 4.4.1. Decisión final en pregunta abierta 1.
- **Tabulaciones del Makefile.** Un editor que convierta tabs en espacios rompe `make`
  (`missing separator`). Mitigación: la prueba del Makefile verifica que las recetas
  empiezan con tabulador.
- **`uv init` sobre un repo existente** podría crear archivos no deseados (README,
  `.gitignore`, `main.py`). Mitigación: revisar `git status`/`git diff` tras T3 y descartar
  lo que sobre.
- **`filterwarnings = error` + plugins** (pytest-cov) pueden emitir `DeprecationWarning`
  y tumbar la suite. Mitigación: si ocurre, filtrar la advertencia concreta con
  comentario, nunca quitar `error`.
- **Finales de línea CRLF** en Windows: `ruff format` usa `line-ending = "auto"`; no
  debería fallar, pero se verifica en T9.
- **Corregir scripts del kit rompe el tablero.** Mitigación: cambios solo de formato y
  cortes de línea; tras T8 se ejecutan `uv run scripts/tablero.py --help`,
  `uv run scripts/auditar_rubrica.py --help` (o su ejecución sin red) y
  `uv run python -m py_compile .claude/hooks/guardia.py` sin errores;
  `git diff --stat` revisado antes del commit.
- **Scripts del kit con PEP 723:** al existir `pyproject.toml`, `uv run scripts/x.py`
  sigue usando el entorno aislado del script (metadatos inline). Se comprueba con
  `uv run scripts/tablero.py --help` en la demo.

## 5. Estrategia de pruebas
| Prueba (archivo::nombre) | Cubre |
|---|---|
| `tests/unit/test_paquete.py::test_version_tiene_formato_semver` | AC-4, AC-1 |
| `tests/unit/test_paquete.py::test_version_coincide_con_pyproject` | AC-4, RF-5 |
| `tests/unit/test_proyecto.py::test_python_fijado_a_313` | AC-1, RF-2, RF-3 |
| `tests/unit/test_proyecto.py::test_build_backend_y_grupo_dev` | AC-1, AC-5, RF-2, RF-4 |
| `tests/unit/test_proyecto.py::test_ruff_reglas_y_convencion_google` | AC-2, RF-6 |
| `tests/unit/test_proyecto.py::test_pytest_testpaths_quiet_y_warnings_error` | AC-1, AC-7, RF-7 |
| `tests/unit/test_proyecto.py::test_makefile_check_corre_ruff_y_pytest` | AC-3, RF-8 |
| `tests/unit/test_proyecto.py::test_sin_requirements_ni_notebooks` | AC-6, RNF-1, RNF-2 |
| `tests/unit/test_proyecto.py::test_ruff_no_excluye_scripts_ni_hooks` | AC-8 (ni `exclude`/`extend-exclude` ni `per-file-ignores` cubren `scripts/` o `.claude/`) |

Todas con patrón AAA (Arrange / Act / Assert comentados), sin red, sin subprocesos.
Verificación manual complementaria (demo, T10): `uv sync --locked`, `uv run ruff check .`,
`uv run ruff format --check .`, `make check`, `uv run scripts/tablero.py --help` (AC-2, AC-3, AC-5, AC-8).

Total planeado: 9 pruebas (piso del backlog: 3).

## 6. Cómo explicarlo en la sustentación
- `pyproject.toml` es el único archivo de configuración: dice qué es el paquete, con qué
  Python corre (3.13), qué herramientas usa (ruff, pytest) y cómo se construye (`uv_build`);
  `uv.lock` congela las versiones exactas para que todos instalen lo mismo con `uv sync`.
- `make check` es la «compuerta de calidad»: primero ruff revisa estilo, imports, tipos
  anotados y docstrings; luego pytest corre las pruebas, y cualquier advertencia cuenta
  como error. Si algo falla, no se abre la PR.
- Las primeras pruebas no prueban el modelo sino el propio proyecto: que la versión sea
  coherente, que Python esté fijado y que no haya `requirements.txt` ni notebooks, es
  decir, que las reglas del curso se cumplen automáticamente.
