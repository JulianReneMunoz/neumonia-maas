---
description: Modo lote — escribe las specs de varias historias seguidas (sin código) para aprobarlas de una vez
argument-hint: SPEC-NNN SPEC-NNN ...
---
Historias: **$ARGUMENTS**

Para cada historia, **en orden y sin escribir código ni pruebas**:
1. `uv run scripts/tablero.py historia <ID>` (verifica que sus dependencias estén en el backlog; no hace falta que estén en Done porque aquí solo se escribe la spec).
2. `git switch develop && git pull --ff-only && git switch -c feature/<NNN>-<slug>`
3. Delega en **spec-writer** la escritura de `specs/<NNN>-<slug>/{spec,plan,tasks}.md`. Si depende de código que aún no existe, que lo anote en «Preguntas abiertas».
4. `git add specs/<NNN>-<slug>/ && git commit -m "docs(spec): <ID> <título corto>"` y `git push -u origin HEAD`.
5. **No muevas la tarjeta** (sigue en Backlog: el WIP y el cycle time empiezan cuando se implementa).

Al terminar todas, `git switch develop` y muestra una tabla: historia · rama · nº de AC · nº de tareas · decisión clave del plan · preguntas abiertas.
Pide al usuario que lea las specs y responda «aprobadas» (o qué cambiar). Con la aprobación, en cada rama cambia `Estado: Borrador` a `Aprobada` y commitea `docs(spec): <ID> aprobada`.
Luego, para cada historia en orden: `git switch feature/<NNN>-<slug>`, **mueve la tarjeta a In Progress** y sigue con `/implementar <ID>` (que hará `git merge develop` primero para traer el código ya fusionado).
