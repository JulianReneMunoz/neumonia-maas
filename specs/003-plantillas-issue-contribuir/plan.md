# Plan · SPEC-003

## 1. Diseño técnico
<!-- Archivos a crear/modificar y firmas públicas. -->
| Archivo | Cambio |
|---|---|
| `.github/ISSUE_TEMPLATE/historia.yml` | **Modificar** (ya existe en el kit). Añadir al inicio de `body` un bloque `type: markdown` que remite a `CONTRIBUTING.md` y a la regla 1:1; añadir `description` al dropdown `puntos` («una sola estimación por historia»). Se conservan los ids `historia`, `ac`, `puntos`, `spec`, `dependencias` y sus `required`. |
| `.github/ISSUE_TEMPLATE/bug.yml` | **Revisar / modificar mínimo.** Ya cumple RF-4 (label `bug`, dos campos obligatorios). Solo se añade `description` a «Spec afectada» si hace falta; ningún id cambia. |
| `.github/ISSUE_TEMPLATE/config.yml` | **Modificar.** Mantener `blank_issues_enabled: false` y añadir `contact_links` con un enlace «Guía de contribución» a `https://github.com/JulianReneMunoz/neumonia-maas/blob/develop/CONTRIBUTING.md` (repo tomado de `docs/tablero.json`). |
| `CONTRIBUTING.md` | **Crear** en la raíz con las 7 secciones de RF-6 (ver §2). |
| `README.md` | **Modificar** una línea en «Enlaces»: `- Cómo contribuir: [CONTRIBUTING.md](CONTRIBUTING.md)`. |
| `.github/PULL_REQUEST_TEMPLATE.md` | **Sin cambios** (RNF-3). |
| `pyproject.toml` / `uv.lock` | `uv add --dev pyyaml` (aprobado; si SPEC-002 ya la añadió, no se toca). |
| `tests/unit/test_plantillas_github.py` | **Opcional** (ver §5). Usa el fixture `raiz_repo` de `tests/conftest.py` (SPEC-001). |

No hay código de producción ni firmas públicas nuevas en `src/`.

## 2. Contratos
**Issue form «Historia de usuario» (`historia.yml`, contrato que verifican AC-1/AC-3/AC-6):**

| id | type | required | Restricción |
|---|---|---|---|
| (sin id) | markdown | — | Enlace a `CONTRIBUTING.md` y regla 1:1 |
| `historia` | textarea | sí | Placeholder «Como …, quiero … para …» |
| `ac` | textarea | sí | Placeholder AC-n con Dado / Cuando / Entonces |
| `puntos` | dropdown | sí | `options` exactamente `["1", "2", "3", "5", "8"]`, sin `multiple` |
| `spec` | input | sí | Placeholder `specs/NNN-slug/` |
| `dependencias` | textarea | no | Placeholder `SPEC-001, … (o ninguna)` |

Claves de nivel superior: `name: Historia de usuario`, `description`, `title: "SPEC-NNN · "`,
`labels: []` (los labels por capa los pone `bootstrap_github.py` o quien crea la historia).

**Issue form «Bug» (`bug.yml`):** `name: Bug`, `labels: ["bug"]`; `pasos` (required),
`esperado` (required), `spec` (opcional).

**`config.yml`:**
```yaml
blank_issues_enabled: false
contact_links:
  - name: Guía de contribución
    url: https://github.com/JulianReneMunoz/neumonia-maas/blob/develop/CONTRIBUTING.md
    about: Flujo SDD, WIP limits, Definition of Done y convenciones del repo.
```

**Esqueleto de `CONTRIBUTING.md`:**
1. `## Flujo de una historia` — diagrama de texto
   `Backlog → spec (spec.md, plan.md, tasks.md) → rama feature/NNN-slug → PR → review → merge a develop → Done`
   y tabla paso → comando (`/siguiente`, `/spec`, `/implementar`, `/pr`, `/revisar`,
   `/fusionar`) → columna de la tarjeta. Incluye que la spec se commitea y aprueba antes del
   código y que la tarjeta pasa a In Progress al empezar a implementar.
2. `## Columnas y WIP limits` — tabla Columna | WIP | Entra cuando… (Backlog sin límite;
   In Progress = nº de integrantes, hoy 1; In Review = 2; Done sin límite) + regla «columna
   llena ⇒ no se empieza otra» + `uv run scripts/tablero.py mover …` respeta el WIP.
3. `## Definition of Done` — lista de seis casillas, idéntica a `CLAUDE.md`.
4. `## Ramas (Gitflow)` — `feature/NNN-slug` desde `develop`, todo por PR, prohibido commit/merge/push directo a `main`/`develop`, `--no-verify` y `push --force`.
5. `## Commits (Conventional Commits)` — tipos `feat`, `fix`, `test`, `docs`, `refactor`, `chore` y 3 ejemplos con el ID (`docs(spec): SPEC-003 spec, plan y tareas`).
6. `## Crear una historia y abrir la PR` — plantilla «Historia de usuario», puntos Fibonacci 1/2/3/5/8, ruta `specs/NNN-slug/`, plantillas SDD en `docs/plantillas-sdd/`; la PR usa `.github/PULL_REQUEST_TEMPLATE.md` con `Closes #N`.
7. `## Reglas no negociables` — resumen en 6 viñetas con enlace a `CLAUDE.md`; métricas del tablero nombradas y remitidas a `uv run scripts/tablero.py metricas`.

## 3. Decisiones de diseño
| Decisión | Alternativas descartadas | Por qué |
|---|---|---|
| **Ajustar** las plantillas del kit en vez de crearlas de cero | Reescribirlas; crear otra plantilla paralela | Ya están en `develop` y cumplen casi todo; reescribir duplica y arriesga romper ids que usan otros scripts. |
| Issue forms (`.yml`) | Plantillas Markdown (`.md`) | Solo los forms permiten `required` y dropdown: es lo que hace «exigible» el AC-1. |
| Puntos como `dropdown` con 1/2/3/5/8 | `input` libre; usar solo el campo «Puntos» del Project | El dropdown impide valores no Fibonacci desde el origen (AC-3); el campo del Project lo sigue llenando `bootstrap_github.py`. |
| `blank_issues_enabled: false` + `contact_links` a CONTRIBUTING | Permitir issues en blanco | Obliga a pasar por una plantilla y deja la guía a un clic (AC-4). |
| `CONTRIBUTING.md` en la raíz | `docs/contributing.md`; `.github/CONTRIBUTING.md` | En la raíz se ve al abrir el repo y GitHub lo enlaza automáticamente al crear issues y PR. |
| WIP escritos como «In Progress = nº de integrantes (hoy 1)» | Escribir solo «1» | Coincide con `ghlib.py`/`tablero.json` y no queda desactualizado si cambia el grupo (AC-7). |
| CONTRIBUTING enlaza la plantilla de PR y `CLAUDE.md` en vez de copiarlas | Copiar su contenido | Una sola fuente de verdad (RNF-3); evita que diverjan. |
| Prueba pytest **opcional** con PyYAML | Sin pruebas; validar con `actionlint`/CLI externa | Barata (< 0,1 s, sin red) y atrapa un `required` borrado por error; PyYAML ya lo usan los scripts del kit (PEP 723), solo faltaría como dev en el proyecto. Una CLI externa añade dependencia fuera de uv. |

## 4. Riesgos
- **Las plantillas se leen solo desde la rama por defecto (`develop`).** El formulario
  definitivo no se ve hasta el merge; mitigación: revisar la vista previa del `.yml` en la
  rama de la PR (GitHub la muestra y marca errores de esquema).
- **Error de esquema silencioso:** un issue form inválido simplemente no aparece en el
  selector. Mitigación: AC-6 (vista previa + prueba opcional que parsea el YAML).
- **Desalineación de WIP** si alguien cambia `integrantes` o `WIP_REVIEW`. Mitigación: la
  guía escribe la regla, no solo el número; la prueba opcional compara los valores.
- **URL fija en `contact_links`** depende del nombre del repo; si se renombra, el enlace se
  rompe. Bajo impacto; se toma de `docs/tablero.json`.
- **`filterwarnings = ["error"]` (SPEC-001):** si PyYAML emitiera advertencias, la prueba
  fallaría; no se esperan con `yaml.safe_load`.

## 5. Estrategia de pruebas
Piso del backlog: **0**. AC-1…AC-8 se verifican por inspección y demo (tabla de abajo). Se
incluye (**aprobado**, Pregunta abierta 2) un archivo de 4 pruebas
AAA, sin red ni GPU, que requiere `uv add --dev pyyaml`:

| Prueba (archivo::nombre) | Cubre |
|---|---|
| `tests/unit/test_plantillas_github.py::test_historia_exige_historia_ac_puntos_y_spec` | AC-1, AC-6 |
| `tests/unit/test_plantillas_github.py::test_historia_puntos_solo_fibonacci` | AC-3 |
| `tests/unit/test_plantillas_github.py::test_bug_y_config_sin_issues_en_blanco` | AC-4, AC-5, AC-6 |
| `tests/unit/test_plantillas_github.py::test_contributing_tiene_flujo_wip_y_dod_coherentes` | AC-2, AC-7, AC-8 |

La última no necesita PyYAML: lee `CONTRIBUTING.md` como texto (busca los encabezados de
RF-6 y la cadena del flujo), `docs/tablero.json` con `json` y compara con `WIP_REVIEW`
leyendo el número del texto de `scripts/ghlib.py` (sin importar el script, que trae su propia
cabecera PEP 723).

Verificación manual (siempre):
| Verificación | Cubre |
|---|---|
| Vista previa de `historia.yml` en GitHub (rama de la PR) sin errores, 4 campos con «*» | AC-1, AC-3, AC-6 |
| Vista previa de `bug.yml` y `config.yml` sin errores | AC-4, AC-5, AC-6 |
| Tras el merge: «New issue» muestra solo Historia, Bug y la guía; intentar enviar vacío | AC-1, AC-3, AC-4, AC-5 |
| Lectura de `CONTRIBUTING.md` contra la lista de RF-6 | AC-2, AC-7, AC-8 |

Total planeado: 4 pruebas (piso del backlog: 0).

## 6. Cómo explicarlo en la sustentación
- Al pulsar «New issue» GitHub muestra un formulario que no deja crear la historia sin
  Como/quiero/para, criterios Given-When-Then, puntos Fibonacci (1, 2, 3, 5 u 8, en una
  lista) y la carpeta de su spec; así cada tarjeta nace cumpliendo la regla 1:1.
- `CONTRIBUTING.md` es el reglamento del equipo en una página: el camino Backlog → spec →
  rama → PR → revisión → merge → Done, cuántas tarjetas caben en cada columna (WIP) y las
  seis condiciones para decir «terminado».
- No inventamos reglas nuevas: la guía resume lo que ya aplican `CLAUDE.md`, los scripts
  del tablero y la plantilla de PR, y enlaza a ellos para que haya una sola fuente de verdad.
