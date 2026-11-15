# Tareas · SPEC-003

<!-- Atómicas, en orden. La primera de cada bloque escribe las pruebas (TDD). -->
<!-- Pregunta abierta 2 aprobada: T1 y T5 se hacen (4 pruebas con PyYAML). -->

### Bloque A · Plantillas de issue
- [x] **T1** `uv add --dev pyyaml` (si aún no está en el grupo dev) y escribir en `tests/unit/test_plantillas_github.py` las pruebas `test_historia_exige_historia_ac_puntos_y_spec`, `test_historia_puntos_solo_fibonacci` y `test_bug_y_config_sin_issues_en_blanco` (AAA, fixture `raiz_repo`) — *Hecho cuando:* `uv run pytest tests/unit/test_plantillas_github.py -q` falla solo por la ausencia de `contact_links` y del bloque `markdown` (lo que aún no existe) · *Cubre:* AC-1, AC-3, AC-4, AC-5, AC-6
- [x] **T2** Ajustar `.github/ISSUE_TEMPLATE/historia.yml`: bloque `markdown` inicial con enlace a `CONTRIBUTING.md` y regla 1:1; `description` del dropdown `puntos`; sin cambiar ids ni `required` — *Hecho cuando:* los campos `historia`, `ac`, `puntos` (opciones `1,2,3,5,8`) y `spec` tienen `required: true`, `dependencias` es opcional y el YAML parsea · *Depende de:* T1 · *Cubre:* AC-1, AC-3, AC-6
- [x] **T3** Revisar `.github/ISSUE_TEMPLATE/bug.yml` (label `bug`, `pasos` y `esperado` obligatorios, `spec` opcional) y ajustar solo descripciones si hace falta — *Hecho cuando:* cumple RF-4 y el YAML parsea · *Cubre:* AC-5, AC-6
- [x] **T4** Añadir `contact_links` «Guía de contribución» a `.github/ISSUE_TEMPLATE/config.yml` manteniendo `blank_issues_enabled: false` — *Hecho cuando:* el YAML parsea y la URL apunta a `CONTRIBUTING.md` en `develop`; las pruebas de T1 pasan · *Depende de:* T2, T3 · *Cubre:* AC-4, AC-6

### Bloque B · Guía de contribución
- [ ] **T5** Escribir `test_contributing_tiene_flujo_wip_y_dod_coherentes` en `tests/unit/test_plantillas_github.py` (encabezados de RF-6, cadena del flujo, WIP = `integrantes` de `docs/tablero.json` y `WIP_REVIEW` de `scripts/ghlib.py`, enlaces de AC-8) — *Hecho cuando:* falla porque `CONTRIBUTING.md` no existe · *Cubre:* AC-2, AC-7, AC-8
- [ ] **T6** Crear `CONTRIBUTING.md` con las secciones 1–3 de RF-6: flujo (diagrama + tabla paso → comando → columna), columnas y WIP limits, Definition of Done (seis puntos de `CLAUDE.md`) — *Hecho cuando:* el texto contiene literalmente «Backlog → spec → rama → PR → review → merge → Done», In Progress = nº de integrantes (hoy 1), In Review = 2 y las seis condiciones de la DoD · *Depende de:* T5 · *Cubre:* AC-2, AC-7
- [ ] **T7** Completar `CONTRIBUTING.md` con las secciones 4–7 de RF-6: Gitflow, Conventional Commits con ejemplos, crear historia / abrir PR (enlaces a `docs/backlog.yaml`, `docs/plantillas-sdd/`, `.github/PULL_REQUEST_TEMPLATE.md`), reglas no negociables (enlace a `CLAUDE.md`) y métricas remitidas a `uv run scripts/tablero.py metricas` — *Hecho cuando:* las 7 secciones existen, los enlaces relativos resuelven y la prueba de T5 pasa · *Depende de:* T6 · *Cubre:* AC-2, AC-8
- [ ] **T8** Añadir en `README.md`, sección «Enlaces», la línea `- Cómo contribuir: [CONTRIBUTING.md](CONTRIBUTING.md)` — *Hecho cuando:* el enlace aparece y resuelve en la vista de GitHub · *Depende de:* T7 · *Cubre:* AC-8

### Bloque C · Cierre
- [ ] **T9** `make check` — *Hecho cuando:* ruff + pytest en verde (incluidas las 4 pruebas de T1 y T5) · *Depende de:* T4, T8 · *Cubre:* RNF-5
- [ ] **T10** Demo local/previa: abrir en GitHub la vista de `historia.yml`, `bug.yml` y `config.yml` en la rama y leer `CONTRIBUTING.md` contra RF-6 — *Hecho cuando:* las tres vistas previas no muestran errores de esquema, los cuatro campos de la historia salen como obligatorios y la lista RF-6 está completa · *Depende de:* T9 · *Cubre:* AC-1…AC-8
- [ ] **T11** Documentación y PR: `Estado: Implementada` en `spec.md`, PR con la plantilla y `Closes #3` — *Hecho cuando:* PR abierta hacia `develop` con título Conventional Commits que incluye SPEC-003 · *Depende de:* T10
- [ ] **T12** Verificación post-merge: en «New issue» comprobar que solo aparecen «Historia de usuario», «Bug» y «Guía de contribución», e intentar enviar una historia vacía — *Hecho cuando:* GitHub bloquea el envío por los campos obligatorios y no hay opción de issue en blanco · *Depende de:* T11 (merge) · *Cubre:* AC-1, AC-3, AC-4, AC-5
