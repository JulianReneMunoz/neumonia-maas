---
description: Paso 2 de SDD — implementa la spec aprobada con TDD, tarea por tarea
argument-hint: SPEC-NNN
---
Historia: **$ARGUMENTS**

1. Verifica las precondiciones; si alguna falla, detente y dilo:
   - estás en la rama `feature/<NNN>-<slug>` de esta historia;
   - `specs/<NNN>-<slug>/spec.md` dice `Estado: Aprobada` y está commiteado
     (`git log --oneline -- specs/<NNN>-<slug>/` muestra el commit `docs(spec)`).
2. Trae lo ya fusionado y asegura el WIP: `git merge develop` (si hay conflicto, resuélvelo y avísame);
   si la tarjeta no está en In Progress, `uv run scripts/tablero.py mover $ARGUMENTS "In Progress"`
   (si el WIP está lleno, detente).
3. Lee spec.md, plan.md y tasks.md. Lee `CLAUDE.md` si no lo tienes en contexto.
4. Por cada tarea de tasks.md, en orden:
   a. escribe primero la(s) prueba(s) (patrón AAA: Arrange / Act / Assert) y comprueba que
      fallan por la razón correcta;
   b. implementa lo mínimo para que pasen;
   c. `uv run ruff check . --fix`, `uv run ruff format .` y `uv run pytest -q`
      (o `make check` si existe);
   d. marca la tarea `- [x]` en tasks.md;
   e. commit con Conventional Commits, p. ej. `feat(api): endpoint /predict (SPEC-012)`.
5. Respeta las capas (inference/ y services/ sin FastAPI) y las reglas de CLAUDE.md.
   Si una tarea exige romper la spec, **detente y pregunta**.
6. Al terminar: `make check` (o ruff + pytest) en verde y, si aplica, una demo local
   (curl a la API, captura de la UI o comando que el usuario pueda repetir).
7. Cambia `Estado: Aprobada` a `Estado: Implementada` en spec.md (commit `docs(spec)`).
8. Explica al usuario en 5 viñetas qué se hizo y por qué, y hazle **una pregunta** de
   comprobación sobre una decisión del plan (lo van a preguntar en la sustentación).
   Luego sugiere `/pr $ARGUMENTS`.
