# Guion de la sustentación (15 min) — anuncio 007, sección 13

Orden fijo: producto → tablero → MLflow → código. Sin diapositivas ni video. Ensáyalo completo
una vez con cronómetro.

## Antes de entrar (todo abierto y listo)
Terminales: `make mlflow` · `make backend` · `make frontend`. Pestañas: app (http://localhost:5173)
con DevTools → Network · `/docs` · tablero (Board) · MLflow Compare · repo en `specs/` · IDE.
Imagen de prueba lista en el escritorio (una NORMAL, una PNEUMONIA, un archivo inválido).

## Minuto a minuto
| Min | Bloque | Qué haces en pantalla |
|---|---|---|
| 0:00–1:30 | Contexto | Problema (apoyo a la lectura de radiografías), modelo `lxyuan/vit-xray-pneumonia-classification@<sha>` (Apache-2.0), alcance y límites. Una frase por cosa. |
| 1:30–6:00 | Demo E2E | Subir PNG → loading → resultado con probabilidad y umbral. Mostrar **Network** (POST /api/v1/predict, JSON). Subir un archivo inválido → error y «Reintentar». Apagar el backend → banner de salud. |
| 6:00–8:00 | Kanban | Board con 4 columnas y WIP en la descripción; abrir una historia (AC, puntos, spec, PR); `gh pr list --state merged --limit 100 \| wc -l` ≥ 40; `find specs -name spec.md \| wc -l` ≥ 40; explicar WIP, throughput, work item age y cycle time con `uv run scripts/tablero.py metricas`. |
| 8:00–10:30 | MLflow | UI viva → experimento `neumonia-vit-eval` → seleccionar los 3 runs → Compare (recall, especificidad, F1, AUC, latencia) → tags, artefactos, Model Registry → mostrar que `/api/v1/model` da la misma revisión. |
| 10:30–12:00 | Backend, terminal, IDE | `uv sync` · `uv run ruff check .` · `uv run pytest -q` (≥ 120) · `/docs` · abrir **una spec** (spec/plan/tasks cerradas) y explicar una decisión de arquitectura **sin leerla**. |
| 12:00–15:00 | Preguntas | Defensa individual: tu parte del código, el modelo, los datos y los sesgos. |

## Preguntas probables (prepara respuesta de 20 segundos)
- ¿Por qué el modelo se carga en `lifespan` y no en cada petición? ¿Qué pasa si falla la carga? (503 en /health)
- ¿Por qué `inference/` no importa FastAPI? (capas; se prueba con `FakeClassifier` sin red)
- ¿Qué cambia entre los 3 runs y cuál elegiste? ¿Por qué? (docs/experimentos.md)
- ¿Con qué datos se entrenó el ViT y por qué evalúas con otro conjunto? (contaminación; RSNA adultos)
- ¿Dónde falla? ¿Qué sesgos hay? (pediátrico vs. adultos, proyección AP/PA; ver Model Card)
- ¿Por qué un umbral de 0.35 y no 0.5? (recall vs. falsos positivos; cifras del run)
- Muéstrame cómo una PR llegó a Done. (issue → spec → rama → PR → review → merge)
- ¿Cómo sabes que la spec se escribió antes del código? (`git log --reverse` de la rama)

## Si algo falla en vivo
No cambies de computador. Muestra repo, tablero y MLflow, y explica qué falló. La transparencia cuenta.
