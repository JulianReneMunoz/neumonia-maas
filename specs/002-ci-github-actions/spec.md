# SPEC-002 · Integración continua con GitHub Actions (ruff + pytest)

- **Estado:** Aprobada <!-- Borrador → Aprobada → Implementada -->
- **Historia:** #2 · **Puntos:** 2 · **Milestone:** M3 · **Labels:** infra, qa
- **Depende de:** SPEC-001
- **PR:** #N (se completa al abrirla)

## 1. Problema y contexto
SPEC-001 deja una compuerta de calidad local (`make check` = ruff + pytest), pero depende
de que cada persona la ejecute antes de abrir la PR. Nada impide hoy fusionar en `develop`
o `main` código que no pasa ruff o que rompe una prueba. Esta historia mueve esa compuerta
a GitHub: cada PR (y cada push a las ramas largas) ejecuta en un runner limpio la misma
instalación con uv y las mismas verificaciones, y publica un check llamado `ci` que la
protección de ramas (`docs/proteccion-rama.json`) exige para fusionar. Para la rúbrica es
el ítem «E8 CI GitHub Actions» y la evidencia de «PR fusionada con checks verdes» de la
Definition of Done.

## 2. Historia
**Como** revisor de código, **quiero** que cada PR ejecute ruff y pytest automáticamente
**para** no fusionar código que rompe la calidad.

## 3. Requisitos
### Funcionales
- RF-1: Existe el workflow `.github/workflows/ci.yml` con un único job cuyo identificador
  es exactamente `ci` (es el nombre del check que exige `docs/proteccion-rama.json`).
- RF-2: El workflow se dispara con `pull_request` hacia `develop` y `main`, y con `push`
  a `develop` y `main`.
- RF-3: El job instala uv con `astral-sh/setup-uv`, con caché de uv habilitada y
  invalidada por `uv.lock`, y Python 3.13.
- RF-4: El job instala dependencias con `uv sync --locked` (falla si `uv.lock` no está al
  día con `pyproject.toml`).
- RF-5: El job ejecuta, en pasos separados y en este orden: `uv run ruff check .`,
  `uv run ruff format --check .` y `uv run pytest` (los mismos comandos que `make check`
  de SPEC-001).
- RF-6: Cualquier paso que termine con código distinto de 0 deja el job, y por tanto el
  check `ci`, en estado fallido (ningún paso usa `continue-on-error`).
- RF-7: Pruebas pytest verifican el contenido del workflow (parsea, job `ci`, disparadores,
  setup-uv, `uv sync --locked`, pasos ruff y pytest).

### No funcionales
- RNF-1: Solo uv: ni `pip`, ni `actions/setup-python`, ni `requirements*.txt`.
- RNF-2: Permisos mínimos del `GITHUB_TOKEN` (`contents: read`); el workflow no usa
  secretos.
- RNF-3: El nombre del check es estable: sin `matrix` ni `name:` en el job que cambien
  el contexto `ci` (una matriz lo convertiría en `ci (3.13)` y la protección no lo
  reconocería).
- RNF-4: Duración del job ≤ 5 min con caché caliente; `timeout-minutes` acotado para que
  un cuelgue no bloquee la PR indefinidamente.
- RNF-5: Las pruebas del workflow no usan red ni ejecutan GitHub Actions; solo leen el
  archivo, siguen el patrón AAA y se integran en `make check`.
- RNF-6: Ejecuciones obsoletas de la misma rama se cancelan (`concurrency`) para no
  gastar minutos ni confundir el estado del check.

## 4. Criterios de aceptación (Given-When-Then)
**AC-1** (backlog)
- **Dado** una PR hacia `develop` o `main`
- **Cuando** se abre o se actualiza
- **Entonces** el workflow CI instala con uv (Python 3.13) y corre ruff y pytest

**AC-2** (backlog)
- **Dado** una prueba que falla
- **Cuando** corre el workflow
- **Entonces** el check queda en rojo y la PR no se puede fusionar

> Verificación de AC-2: la parte «check en rojo» la garantiza el workflow (RF-6) y se
> comprueba con una PR de prueba con un test roto. La parte «no se puede fusionar»
> depende de aplicar `docs/proteccion-rama.json` a `develop` y `main` **después** de
> fusionar esta historia (el check `ci` tiene que haber corrido al menos una vez para
> poder exigirlo). La evidencia es `gh pr view <n> --json mergeStateStatus` = `BLOCKED`
> y la captura del botón de merge deshabilitado; la PR de prueba se cierra sin fusionar.
> Ver plan §5 y tareas T9–T10.

**AC-3** (añadido: lock desactualizado)
- **Dado** una PR que modifica `pyproject.toml` sin regenerar `uv.lock`
- **Cuando** corre el workflow
- **Entonces** el paso `uv sync --locked` falla y el check `ci` queda en rojo antes de
  ejecutar ruff y pytest

**AC-4** (añadido: formato)
- **Dado** una PR con un archivo `.py` que pasa `ruff check` pero no está formateado
- **Cuando** corre el workflow
- **Entonces** el paso `ruff format --check` falla y el check `ci` queda en rojo

**AC-5** (añadido: push a ramas largas)
- **Dado** una PR fusionada en `develop` (o en `main`)
- **Cuando** llega el push resultante a esa rama
- **Entonces** el workflow vuelve a correr sobre el código integrado y su resultado queda
  visible en el historial de la rama

**AC-6** (añadido: nombre del check)
- **Dado** el archivo `.github/workflows/ci.yml`
- **Cuando** las pruebas lo parsean
- **Entonces** existe exactamente un job, con id `ci`, sin `matrix`, sin
  `continue-on-error` y con permisos `contents: read`

## 5. Fuera de alcance
- Umbral de cobertura en CI (`--cov-fail-under 85`): SPEC-033.
- Hooks de pre-commit: SPEC-036. Dockerfile y build de imagen: SPEC-035.
- Badge de CI en el README: SPEC-037 (aquí solo una línea que explica el workflow).
- Jobs de frontend (pnpm, tsc, vitest): los añadirá la historia del frontend que los
  necesite, como pasos dentro del mismo job `ci` o con su propio check.
- Pipeline de GitLab CI/CD y despliegue: SPEC-041 en adelante (M4).
- Aplicar la protección de ramas no es código de esta PR: es un paso operativo posterior
  a la fusión (ARRANQUE.md §6) que se usa para evidenciar AC-2.

## 6. Métricas de éxito
- La PR de esta historia muestra el check `ci` en verde antes de fusionarse.
- PR de prueba con test roto: check `ci` en rojo y `mergeStateStatus = BLOCKED` tras
  aplicar la protección.
- Duración del job ≤ 5 min con caché caliente (se lee en la pestaña Actions).
- ≥ 2 pruebas nuevas en verde en `make check` (plan: 7).

## 7. Preguntas abiertas
1. **SPEC-001 aún no está en `develop`.** El `pyproject.toml`, `uv.lock`,
   `.python-version`, el Makefile y la fixture `raiz_repo` de `tests/conftest.py` solo
   existen en la spec de `feature/001-esqueleto-uv`. Antes de implementar, esta rama
   trae `develop` con merge una vez fusionada SPEC-001 (T1 lo verifica); sin rebase,
   porque la rama ya está en el remoto y `push --force` está prohibido. Si la
   fixture cambia de nombre, se adapta el plan.
Resueltas en la aprobación (14/11/2026):
2. **PyYAML como dependencia dev:** aceptada (`uv add --dev pyyaml`).
3. **Protección de ramas:** el repo es **privado** por ahora. Se intenta aplicar la
   protección (T9); si GitHub no lo permite, AC-2 se demuestra con una **PR en borrador**
   con un test roto cuyo check `ci` queda en rojo, y se cierra sin fusionar (T10). Esa PR
   no cuenta como una de las 40.
4. **Acciones:** se fijan por etiqueta de versión mayor (la vigente al implementar, T4).
5. **Número del issue:** #2 (igual al número de la spec).
