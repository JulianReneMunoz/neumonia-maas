# Tareas · SPEC-002

<!-- Atómicas, en orden. La primera de cada bloque escribe las pruebas (TDD). -->

### Bloque 0 · Preparación
- [x] **T1** Traer `develop` (con SPEC-001 ya fusionada) a `feature/002-ci-github-actions` con merge, sin rebase ni `push --force` — *Hecho cuando:* existen `pyproject.toml`, `uv.lock`, `.python-version`, `Makefile` y la fixture `raiz_repo` en `tests/conftest.py`, y `make check` está en verde antes de tocar nada · *Cubre:* precondición de todos los AC
- [ ] **T2** Añadir PyYAML al grupo dev con `uv add --dev pyyaml` — *Hecho cuando:* `pyproject.toml` y `uv.lock` cambian solo en esa dependencia y `uv sync --locked` termina sin error · *Depende de:* T1 · *Cubre:* RF-7

### Bloque 1 · Workflow (TDD)
- [ ] **T3** Escribir `tests/unit/test_ci.py` con las 7 pruebas del plan §5 (fixture `workflow_ci`, helpers `_comandos_run` y `_disparadores` con el caso `on` → `True` comentado) — *Hecho cuando:* `uv run pytest tests/unit/test_ci.py` falla porque `.github/workflows/ci.yml` no existe (no por errores de import o sintaxis) · *Depende de:* T2 · *Cubre:* AC-1, AC-2, AC-3, AC-4, AC-5, AC-6
- [ ] **T4** Verificar la versión mayor vigente de `actions/checkout` y `astral-sh/setup-uv` y anotarla en el plan si difiere de `@v5`/`@v6` — *Hecho cuando:* las dos etiquetas están confirmadas (enlace a su página de releases en el cuerpo de la PR) · *Depende de:* T3
- [ ] **T5** Crear `.github/workflows/ci.yml` según el contrato del plan §2 — *Hecho cuando:* las 7 pruebas de T3 pasan · *Depende de:* T4 · *Cubre:* AC-1, AC-3, AC-4, AC-5, AC-6
- [ ] **T6** Comprobar a mano que la prueba de fallos detecta un retroceso: añadir temporalmente `continue-on-error: true` a un paso y luego quitar `--locked` — *Hecho cuando:* en cada caso falla la prueba esperada y, al revertir, todo vuelve a verde (`git diff` vacío en el YAML respecto a T5) · *Depende de:* T5 · *Cubre:* AC-2, AC-3

### Bloque 2 · Calidad, documentación y PR
- [ ] **T7** `make check` y demo local — *Hecho cuando:* ruff + pytest en verde (pruebas de SPEC-001 + 7 nuevas) y `uv run python -c "import yaml, pathlib; print(list(yaml.safe_load(pathlib.Path('.github/workflows/ci.yml').read_text())['jobs']))"` imprime `['ci']` · *Depende de:* T6
- [ ] **T8** Documentación y PR — *Hecho cuando:* README tiene el párrafo «Integración continua», la spec pasa a `Estado: Implementada`, la PR está abierta con `Closes #2` y `gh pr checks <n>` muestra `ci` en verde (si falla solo en Linux, se corrige aquí antes de seguir) · *Depende de:* T7 · *Cubre:* AC-1

### Bloque 3 · Verificación posterior a la fusión (AC-2, AC-5)
- [ ] **T9** Tras fusionar la PR: confirmar el push a `develop` y aplicar la protección — *Hecho cuando:* `gh run list --branch develop --workflow CI` muestra una ejecución en verde del commit de merge y los dos `gh api -X PUT …/branches/{develop,main}/protection --input docs/proteccion-rama.json` de ARRANQUE.md §6 responden sin error (si GitHub lo rechaza por el plan del repo, se guarda el mensaje como evidencia y se avisa al usuario) · *Depende de:* T8 · *Cubre:* AC-5, AC-2
- [ ] **T10** PR de prueba con test roto (en **borrador**, `gh pr create --draft`; no cuenta como una de las 40) — *Hecho cuando:* una rama `chore/prueba-ci-rojo` desde `develop` con un test `assert False` abre una PR en borrador cuyo check `ci` queda en rojo en el paso «Pytest» (captura guardada para la sustentación); si T9 aplicó la protección, además `gh pr view <m> --json mergeStateStatus` devuelve `BLOCKED`; la PR se cierra sin fusionar y la rama se borra · *Depende de:* T9 · *Cubre:* AC-2
