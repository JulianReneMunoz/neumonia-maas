---
description: Fusiona una PR revisada con checks verdes y mueve la tarjeta a Done
argument-hint: <número de PR>
---
PR: **#$ARGUMENTS**

1. Verifica todo; si algo falla, detente y dilo:
   - `gh pr checks $ARGUMENTS` → todos los checks en verde;
   - la PR tiene una revisión (aprobación de otra persona o comentario de revisión con
     veredicto APROBAR);
   - el cuerpo tiene `Closes #N` y el enlace a la spec;
   - la base es `develop`.
2. `gh pr merge $ARGUMENTS --merge --delete-branch`
3. Obtén el SPEC-NNN del título y mueve la tarjeta:
   `uv run scripts/tablero.py mover SPEC-NNN Done`.
4. Actualiza tu copia local:
   ```
   git switch develop
   git pull --ff-only
   ```
5. Muestra `uv run scripts/tablero.py metricas` (WIP, throughput, cycle time) y sugiere
   `/siguiente`.
