# Plan · SPEC-002

## 1. Diseño técnico
| Archivo | Cambio |
|---|---|
| `.github/workflows/ci.yml` | **Crear.** Workflow «CI» con un job `ci` (ver contrato §2). |
| `pyproject.toml` / `uv.lock` | **Modificar** solo con `uv add --dev pyyaml` (grupo `dev`). Nada a mano. |
| `tests/unit/test_ci.py` | **Crear.** 7 pruebas AAA que leen y parsean el workflow; fixture local `workflow_ci`. |
| `tests/conftest.py` | **Sin cambios:** se reutiliza la fixture `raiz_repo() -> Path` de SPEC-001. |
| `README.md` | **Modificar** mínimamente: en «Instalación y calidad» (de SPEC-001), un párrafo «Integración continua» que dice qué corre el job `ci`, que es el mismo `make check` y cómo verlo (`gh pr checks <n>`). |
| `Makefile` | **Sin cambios.** El CI llama a los mismos comandos `uv run …` que `lint` y `test`. |

### Firmas (solo pruebas; no hay código de producción)
```python
# tests/unit/test_ci.py
RUTA_WORKFLOW: Final = Path(".github") / "workflows" / "ci.yml"


@pytest.fixture
def workflow_ci(raiz_repo: Path) -> dict[Any, Any]:
    """Workflow de CI parseado con yaml.safe_load."""


def _comandos_run(workflow: dict[Any, Any]) -> list[str]:
    """Lista ordenada de los `run:` del job `ci`."""


def _disparadores(workflow: dict[Any, Any]) -> dict[str, Any]:
    """Sección `on:` (PyYAML 1.1 la lee como clave `True`)."""
```

## 2. Contratos
**`.github/workflows/ci.yml` (contrato que verifican las pruebas):**
```yaml
name: CI

on:
  pull_request:
    branches: [develop, main]
  push:
    branches: [develop, main]

permissions:
  contents: read

concurrency:
  group: ci-${{ github.ref }}
  cancel-in-progress: ${{ github.event_name == 'pull_request' }}

jobs:
  ci:                       # id = nombre del check exigido por docs/proteccion-rama.json
    runs-on: ubuntu-latest
    timeout-minutes: 10
    steps:
      - uses: actions/checkout@v7          # mayor vigente (v7.0.1, 20/07/2026)
      - uses: astral-sh/setup-uv@v10.3.3   # sin etiqueta flotante v10: versión exacta (pregunta abierta 4)
        with:
          enable-cache: true
          cache-dependency-glob: uv.lock
          python-version: "3.13"
      - name: Instalar dependencias (lock exacto)
        run: uv sync --locked
      - name: Ruff (lint)
        run: uv run ruff check .
      - name: Ruff (formato)
        run: uv run ruff format --check .
      - name: Pytest
        run: uv run pytest
```

**Check publicado:** contexto `ci` (estado `success` / `failure`), uno por commit de la PR.

**Reglas que verifican las pruebas:**
- `jobs` tiene exactamente una clave: `ci`; sin `strategy.matrix`, sin `name`, sin
  `continue-on-error` en el job ni en sus pasos.
- `on.pull_request.branches` y `on.push.branches` ⊇ `{develop, main}`.
- Hay un paso `uses: astral-sh/setup-uv@…` con `enable-cache: true` y
  `python-version` igual al contenido de `.python-version` (`3.13`).
- Ningún `uses` es `actions/setup-python`; ningún `run` contiene `pip`.
- Orden de `run`: `uv sync --locked` < `uv run ruff check .` < `uv run ruff format --check .`
  < `uv run pytest`.
- `permissions == {"contents": "read"}`.

## 3. Decisiones de diseño
| Decisión | Alternativas descartadas | Por qué |
|---|---|---|
| Un solo job con id `ci`, sin matriz ni `name:` | Matriz de SO/Python; jobs separados `lint` y `test` | GitHub usa el `name` (o el id) del job como contexto del check; con matriz sería `ci (3.13)` y con dos jobs habría dos checks, y `docs/proteccion-rama.json` exige exactamente `ci`. Un solo Python (3.13) es lo que exige el curso. |
| Pasos separados (`ruff check`, `ruff format --check`, `pytest`) en vez de `make check` | `run: make check` | En la pestaña Actions se ve de inmediato qué compuerta falló; además no depende de `make`. Los comandos son idénticos a los del Makefile, así que local y CI no divergen. |
| `astral-sh/setup-uv` con `enable-cache` y `cache-dependency-glob: uv.lock` | `actions/setup-python` + `pip install uv`; `actions/cache` manual | Regla «solo uv» (nada de pip); setup-uv instala uv y gestiona la caché, que se invalida cuando cambia el lock. |
| Python vía `python-version: "3.13"` de setup-uv (uv descarga su Python gestionado) | `actions/setup-python`; confiar solo en `.python-version` | Queda explícito en el YAML (lo revisa el profesor) y una prueba garantiza que coincide con `.python-version`, así no hay dos fuentes que diverjan. |
| `uv sync --locked` | `uv sync`; `uv sync --frozen` | `--locked` falla si el lock no corresponde al `pyproject.toml` (AC-3); `uv sync` lo regeneraría en silencio y `--frozen` no verificaría la coherencia. |
| Disparadores `pull_request` **y** `push` a `develop`/`main` | Solo `pull_request` | El push valida el resultado real de la fusión (AC-5), deja historial verde en la rama y será la fuente del badge de SPEC-037. Sin `push` a ramas `feature/*`: la PR ya corre y se evita duplicar ejecuciones. |
| `permissions: contents: read` y `concurrency` con cancelación | Permisos por defecto; sin concurrencia | Mínimo privilegio (el job solo lee el código) y no se acumulan ejecuciones viejas cuando se empujan varios commits seguidos. |
| Cancelar solo en `pull_request` (`cancel-in-progress: ${{ github.event_name == 'pull_request' }}`) — *ajuste tras la revisión de la PR #47* | `cancel-in-progress: true` para todo | Con `true`, dos merges seguidos a `develop` comparten grupo (`ci-refs/heads/develop`) y el segundo cancela el run del primero, que queda sin evidencia verde (AC-5). En una PR sí conviene cancelar: el run viejo ya no describe el código actual. |
| Prohibir `if:` en el job y en los pasos, y `permissions` propios del job — *ajuste tras la revisión de la PR #47* | Confiar en la revisión humana | Un `if: false` deja el check `ci` en *skipped*, que la protección de ramas da por cumplido; un `permissions: write-all` en el job anula el mínimo privilegio del workflow. Las pruebas lo detectan. |
| Pruebas con PyYAML (`yaml.safe_load`), añadida con `uv add --dev pyyaml` | Buscar cadenas en el texto; `ruamel.yaml` | El AC del backlog pide «el YAML parsea»: solo un parser real lo comprueba. PyYAML es la opción más conocida y basta para leer; `ruamel` añade complejidad sin beneficio aquí. |
| Las pruebas no ejecutan el workflow (ni `act` ni red) | `act` local en Docker | Regla «sin red» y sin Docker en las pruebas; el comportamiento real se verifica en la propia PR (check verde) y en la PR de prueba (check rojo). |

## 4. Riesgos
- **`on:` como booleano.** PyYAML implementa YAML 1.1 y lee la clave `on` como `True`.
  Mitigación: el helper `_disparadores` busca `"on"` o `True`; está comentado para
  explicarlo en la sustentación.
- **SPEC-001 sin fusionar.** Sin `uv.lock` ni `pyproject.toml` en la rama, el workflow
  falla en `uv sync --locked`. Mitigación: T1 trae `develop` (con SPEC-001
  ya fusionada) con merge; nunca rebase, porque la rama ya está en el remoto y
  `push --force` está prohibido.
- **Diferencias Windows ↔ Linux** (CRLF, rutas, `filterwarnings = error` con otra
  plataforma). Mitigación: la primera ejecución en la PR de esta historia es la prueba;
  si algo falla solo en Linux, se corrige en esta PR antes de fusionar.
- **Versión de las acciones.** Una etiqueta mayor puede no existir o quedar obsoleta.
  Mitigación: verificar la mayor vigente de `actions/checkout` y `astral-sh/setup-uv`
  al implementar (T4); la prueba solo exige el prefijo `astral-sh/setup-uv@`.
- **Protección de ramas no disponible** (repo privado, plan gratuito). Mitigación:
  documentar la respuesta de la API y usar como evidencia el check rojo + `/fusionar`,
  que se niega a fusionar sin checks verdes (pregunta abierta 3).
- **`strict: true` en la protección** obliga a que la rama esté al día con `develop`
  antes de fusionar; puede pedir traer `develop` otra vez (con merge, sin rebase). Se acepta: es lo que garantiza que el
  check verde corresponda al código integrado.

## 5. Estrategia de pruebas
| Prueba (archivo::nombre) | Cubre |
|---|---|
| `tests/unit/test_ci.py::test_workflow_parsea_y_tiene_unico_job_ci` | AC-6, AC-1, RF-1 |
| `tests/unit/test_ci.py::test_disparadores_pr_y_push_a_develop_y_main` | AC-1, AC-5, RF-2 |
| `tests/unit/test_ci.py::test_setup_uv_con_cache_y_python_igual_a_python_version` | AC-1, RF-3, RNF-1 |
| `tests/unit/test_ci.py::test_pasos_en_orden_sync_locked_ruff_format_pytest` | AC-1, AC-3, AC-4, RF-4, RF-5 |
| `tests/unit/test_ci.py::test_ningun_paso_ignora_fallos` | AC-2, RF-6 |
| `tests/unit/test_ci.py::test_sin_pip_ni_setup_python` | RNF-1 |
| `tests/unit/test_ci.py::test_permisos_minimos_y_sin_matrix` (también permisos del job) | AC-6, RNF-2, RNF-3 |
| `tests/unit/test_ci.py::test_job_y_pasos_sin_condiciones_if` (añadida en la revisión) | AC-2, RF-6 |
| `tests/unit/test_ci.py::test_concurrency_solo_cancela_en_pull_request` (añadida en la revisión) | AC-5, RNF-6 |

Todas con patrón AAA (Arrange / Act / Assert comentados), sin red y sin subprocesos.

**Verificación en GitHub (no automatizable en pytest):**
| Verificación | Cubre | Evidencia |
|---|---|---|
| La PR de esta historia muestra `ci` en verde | AC-1 | `gh pr checks <n>` |
| Tras fusionar, el push a `develop` dispara `ci` | AC-5 | `gh run list --branch develop --workflow CI` |
| PR de prueba `chore/prueba-ci-rojo` (desde `develop`) con un `assert False` en un test nuevo: `ci` en rojo | AC-2 | `gh pr checks <m>` con `fail` en el paso «Pytest» |
| Con `docs/proteccion-rama.json` aplicado a `develop` y `main`, esa PR queda bloqueada | AC-2 | `gh pr view <m> --json mergeStateStatus` = `BLOCKED` + captura del botón; se cierra la PR sin fusionar y se borra la rama |
| (opcional) misma PR de prueba con `pyproject.toml` alterado sin lock, o un `.py` sin formato | AC-3, AC-4 | paso «Instalar dependencias» o «Ruff (formato)» en rojo |

Total planeado: 9 pruebas (7 iniciales + 2 de la revisión de la PR #47; piso del backlog: 2).

## 6. Cómo explicarlo en la sustentación
- El archivo `.github/workflows/ci.yml` le dice a GitHub: «en cada PR hacia `develop` o
  `main`, y en cada push a ellas, prende una máquina Linux limpia, instala uv y Python
  3.13, instala exactamente lo que dice `uv.lock` y corre ruff y pytest», es decir, el
  mismo `make check` que corremos en local.
- El job se llama `ci` porque ese es el nombre que exige la protección de ramas: si el
  check `ci` está en rojo (una prueba falla, el código no tiene formato o el lock está
  desactualizado), GitHub deshabilita el botón de merge. Lo demostramos con una PR de
  prueba con un test roto.
- Las pruebas de `tests/unit/test_ci.py` revisan el propio workflow: que el YAML sea
  válido, que tenga el job `ci`, que use uv con `--locked` y que ningún paso ignore
  errores, para que nadie lo «arregle» desactivando la compuerta sin que se note.
