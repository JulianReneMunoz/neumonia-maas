---
description: Paso 1 de SDD — crea la rama y escribe spec.md, plan.md y tasks.md ANTES de cualquier código
argument-hint: SPEC-NNN
---
Historia: **$ARGUMENTS**

Sigue estos pasos en orden. **No escribas código de producción ni pruebas en este comando.**

1. Muestra la historia: `uv run scripts/tablero.py historia $ARGUMENTS`. Verifica que sus
   dependencias estén en *Done*; si no, detente y dilo.
2. Prepara la rama desde develop actualizado:
   ```
   git switch develop
   git pull --ff-only
   git switch -c feature/<NNN>-<slug>
   ```
   (NNN y slug salen del backlog; ej. `feature/005-contrato-clasificador-carga`).
3. Mueve la tarjeta: `uv run scripts/tablero.py mover $ARGUMENTS "In Progress"`.
   Si el script rechaza el movimiento por el WIP limit, detente.
4. Delega al subagente **spec-writer** la escritura de `specs/<NNN>-<slug>/spec.md`,
   `plan.md` y `tasks.md` a partir de `docs/plantillas-sdd/` y de la historia del backlog.
   Debe leer el código actual para que el plan encaje con lo que ya existe.
5. Revisa lo que escribió: cada AC del backlog aparece en Given-When-Then, cada AC tiene
   al menos una prueba en la estrategia de pruebas, y cada tarea de `tasks.md` es
   verificable. El número de pruebas planeadas debe ser ≥ el campo `pruebas` del backlog.
6. Commit **solo** de la spec:
   ```
   git add specs/<NNN>-<slug>/
   git commit -m "docs(spec): <SPEC-NNN> <título corto>"
   ```
7. **Detente.** Muestra al usuario un resumen (problema, AC, decisiones del plan, tareas)
   y pídele que lea `specs/<NNN>-<slug>/spec.md` y responda «aprobada» o pida cambios.
   Cuando apruebe, cambia `Estado: Borrador` a `Estado: Aprobada` en spec.md y haz
   commit `docs(spec): <SPEC-NNN> aprobada`. Luego sugiere `/implementar $ARGUMENTS`.
