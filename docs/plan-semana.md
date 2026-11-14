# Plan hasta la sustentación del jueves 19/11 — neumonía MaaS

**Meta:** todo fusionado y ensayado el **miércoles 18/11 en la noche**. Hoy es sáb 14/11: quedan ~4 días y medio, así que el ritmo es **~9 PRs/día** (≈ 35–45 min por historia con Claude Code). Una historia activa a la vez (WIP = 1).

> Tu cuello de botella no es Claude: es **leer y aprobar cada spec** (≈ 3–5 min) y **responder la pregunta de comprobación**. Usa el modo lote (`/lote`, ver abajo).


## Sáb 14/11 · noche — Arranque + cimientos (uv, CI, plantillas, config)

| Spec | Historia | Pts | Pruebas ≥ | Depende de |
|---|---|---|---|---|
| SPEC-001 | Esqueleto del proyecto con uv y Python 3.13 | 2 | 3 | — |
| SPEC-002 | Integración continua con GitHub Actions (ruff + pytest) | 2 | 2 | SPEC-001 |
| SPEC-003 | Plantillas de historia de usuario y guía de contribución | 1 | 0 | SPEC-001 |
| SPEC-004 | Configuración tipada con pydantic-settings | 2 | 5 | SPEC-001 |

**Cierre:** 4 PRs · 7 pts · **acumuladas 4** · `make check` en verde · tarjetas en Done.


## Dom 15/11 — Inferencia (modelo HF) + capa de servicio + app FastAPI + errores

| Spec | Historia | Pts | Pruebas ≥ | Depende de |
|---|---|---|---|---|
| SPEC-005 | Contrato del clasificador y carga única del modelo MaaS | 5 | 6 | SPEC-004 |
| SPEC-006 | Preprocesamiento separado y configurable (RGB, tamaño, CLAHE opcional) | 3 | 10 | SPEC-005 |
| SPEC-007 | Postprocesamiento y umbral de decisión configurable | 2 | 6 | SPEC-005 |
| SPEC-008 | Lectura segura de imágenes (PNG/JPEG/DICOM) y rechazo de inválidas | 3 | 6 | SPEC-006 |
| SPEC-009 | Capa de servicio DiagnosisService (orquestación y latencia) | 3 | 6 | SPEC-007, SPEC-008 |
| SPEC-010 | App FastAPI con lifespan (carga única) y /health | 3 | 4 | SPEC-009 |
| SPEC-011 | Schemas tipados de respuesta y error con Pydantic | 2 | 6 | SPEC-010 |
| SPEC-012 | Endpoint POST /api/v1/predict (multipart) | 3 | 6 | SPEC-011 |
| SPEC-013 | Manejo de errores HTTP, límite de tamaño y timeout | 3 | 10 | SPEC-012 |

**Cierre:** 9 PRs · 27 pts · **acumuladas 13** · `make check` en verde · tarjetas en Done.


## Lun 16/11 — API restante + fixtures + frontend core (carga, estados, resultado)

| Spec | Historia | Pts | Pruebas ≥ | Depende de |
|---|---|---|---|---|
| SPEC-014 | CORS para el frontend y versionado de la API | 1 | 3 | SPEC-012 |
| SPEC-015 | Logging estructurado con request_id y latencia | 2 | 4 | SPEC-012 |
| SPEC-016 | Endpoints /api/v1/model y /api/v1/metrics | 2 | 4 | SPEC-015 |
| SPEC-017 | Fixtures compartidas y datos sintéticos (sin red ni GPU) | 2 | 5 | SPEC-008 |
| SPEC-018 | Frontend React + TypeScript con Vite y pnpm | 2 | 0 | SPEC-014 |
| SPEC-019 | Cliente HTTP tipado con timeout y errores | 3 | 0 | SPEC-018 |
| SPEC-020 | Componente de carga de imagen con vista previa y validación | 3 | 0 | SPEC-018 |
| SPEC-021 | Estados idle / loading / success / error con reintento | 3 | 0 | SPEC-019, SPEC-020 |
| SPEC-022 | Tarjeta de resultado con confianza, umbral y latencia | 2 | 0 | SPEC-021 |

**Cierre:** 9 PRs · 20 pts · **acumuladas 22** · `make check` en verde · tarjetas en Done.


## Mar 17/11 — Frontend final + MLflow completo (3 runs, Registry) + integración

| Spec | Historia | Pts | Pruebas ≥ | Depende de |
|---|---|---|---|---|
| SPEC-023 | Indicador de salud del backend | 2 | 0 | SPEC-019 |
| SPEC-024 | Historial de análisis de la sesión | 2 | 0 | SPEC-022 |
| SPEC-025 | Accesibilidad y diseño responsive | 2 | 0 | SPEC-022 |
| SPEC-026 | Panel «Acerca del modelo» y aviso de uso | 2 | 0 | SPEC-016, SPEC-019 |
| SPEC-027 | Servidor MLflow local y módulo de tracking | 3 | 4 | SPEC-004 |
| SPEC-028 | Dataset de evaluación independiente con manifiesto versionado | 3 | 5 | SPEC-008 |
| SPEC-029 | Script de evaluación con métricas de calidad y latencia en MLflow | 5 | 6 | SPEC-027, SPEC-028, SPEC-009 |
| SPEC-030 | Tres runs comparables en el mismo experimento | 3 | 3 | SPEC-029 |
| SPEC-031 | Registro del modelo en MLflow Model Registry | 3 | 4 | SPEC-030 |
| SPEC-032 | Pruebas de integración del flujo completo de la API | 3 | 10 | SPEC-013, SPEC-017 |

**Cierre:** 10 PRs · 28 pts · **acumuladas 32** · `make check` en verde · tarjetas en Done.


## Mié 18/11 — Calidad, Docker, README, Model Card, Archify, limpieza, ficha y ENSAYO

| Spec | Historia | Pts | Pruebas ≥ | Depende de |
|---|---|---|---|---|
| SPEC-033 | Cobertura mínima de 85 % en CI | 2 | 6 | SPEC-032 |
| SPEC-034 | Prueba de contrato OpenAPI | 2 | 4 | SPEC-016 |
| SPEC-035 | Imagen Docker CPU multi-stage y docker compose | 3 | 3 | SPEC-012, SPEC-018 |
| SPEC-036 | Hooks de pre-commit (ruff, formato, archivos grandes, secretos) | 1 | 0 | SPEC-001 |
| SPEC-037 | README con badges, arquitectura, instalación y uso | 2 | 1 | SPEC-035 |
| SPEC-038 | Model Card formal en docs/model-card.md | 3 | 2 | SPEC-031 |
| SPEC-039 | Diagrama de arquitectura (Archify) y ADRs | 2 | 1 | SPEC-035 |
| SPEC-040 | Cero warnings, type hints y docstrings completos | 2 | 4 | SPEC-033 |

**Cierre:** 8 PRs · 17 pts · **acumuladas 40** · `make check` en verde · tarjetas en Done.


## Después del jue 19/11 — M4 provisional (GitLab CI/CD, Droplet, post-mortem) — sustentación M4: sáb 28/11

| Spec | Historia | Pts | Pruebas ≥ | Depende de |
|---|---|---|---|---|
| SPEC-041 | Pipeline GitLab CI/CD con compuertas de calidad | 5 | 0 | SPEC-033, SPEC-035 |
| SPEC-042 | Credenciales como variables protegidas y enmascaradas | 2 | 0 | SPEC-041 |
| SPEC-043 | Despliegue en Droplet con docker compose | 5 | 0 | SPEC-042 |
| SPEC-044 | Verificación post-despliegue y rollback | 3 | 0 | SPEC-043 |
| SPEC-045 | Post-mortem de un incidente de despliegue | 2 | 0 | SPEC-044 |

**Cierre:** 5 PRs · 17 pts.


## Modo lote (para llegar a 9 PRs/día sin saltarse el SDD)
Cada mañana (o noche anterior), en Claude Code:
1. `/lote SPEC-005 SPEC-006 SPEC-007 SPEC-008` → por cada historia crea su rama y su spec/plan/tasks, los commitea (`docs(spec)`) **sin escribir código** y **sin mover la tarjeta**. Tú lees las specs de corrido y dices «aprobadas» (o pides cambios).
2. Luego, una a una: `/implementar` → `/pr` → `/revisar` → `/fusionar`. Al empezar a implementar, la tarjeta pasa a In Progress (así el WIP y el cycle time siguen siendo reales).
La spec sigue siendo anterior al código **en cada rama** (`git log --reverse` lo demuestra). Si una spec depende de código que aún no existe, el `spec-writer` lo anota en «Preguntas abiertas» y se ajusta al implementar con un commit `docs(spec): ajuste …`.

## Ruta crítica (si el reloj aprieta, esto manda sobre el conteo de PRs)
La demo E2E pesa 25 % y MLflow 20 %: sin ellos no hay nota, aunque haya 40 PRs. **Prioridad:** (1) SPEC-001…013 backend servible, (2) SPEC-018…022 frontend funcional, (3) SPEC-027…031 MLflow con 3 runs, (4) todo lo demás. Las historias de «volumen» (docs, QA, infra: 033–040) son rápidas y se pueden hacer el miércoles, pero **el miércoles ya no se abre trabajo nuevo después de las 6 p. m.**: la noche es para `/ensayo` y el ensayo cronometrado.
Si el martes en la noche vas por debajo de 31 PRs, avísame y recortamos juntos: es mejor 36 PRs con demo completa que 40 con demo rota, pero el piso de 40 afecta dos categorías (30 %), así que se decide con el profesor.

## Hitos que no se pueden dejar para el final
- **Sáb 14:** repo, tablero e issues creados (ARRANQUE.md) y SPEC-001/002 fusionadas; luego protección de ramas.
- **Dom 15:** SHA del modelo fijado (SPEC-005) — todo lo demás cita ese `org/modelo@rev`. Descarga de los pesos (~330 MB) con buena conexión.
- **Mar 17:** los 3 runs de MLflow; evaluación sobre RSNA (los datos de `C:\Neumonia\data\raw\rsna` del proyecto anterior se reutilizan con `scripts/preparar_eval.py`).
- **Mié 18:** `uv sync` + `uv run pytest -q` en carpeta limpia, `docker compose up`, ficha enviada y ensayo de 15 min con cronómetro.
