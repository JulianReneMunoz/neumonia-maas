---
description: Paso 3 de SDD — abre la PR hacia develop con la plantilla, Closes #N y enlace a la spec
argument-hint: SPEC-NNN
---
Historia: **$ARGUMENTS**

1. Comprueba: todas las tareas de `specs/<NNN>-<slug>/tasks.md` están `[x]`, `make check`
   (o ruff + pytest) en verde y `git status` limpio.
2. Obtén el número del issue: `uv run scripts/tablero.py issue $ARGUMENTS`.
3. `git push -u origin HEAD`
4. Crea la PR con el cuerpo basado en `.github/PULL_REQUEST_TEMPLATE.md`, completando todas
   las secciones (qué cambia, por qué, cómo se probó con la salida real de pytest, riesgos,
   cómo explicarlo):
   ```
   gh pr create --base develop \
     --title "<tipo>(<ámbito>): <descripción> (<SPEC-NNN>)" \
     --body-file <archivo temporal fuera del repo> \
     --label <labels de la historia> --milestone M3
   ```
   El cuerpo debe incluir `Closes #<issue>` y el enlace a `specs/<NNN>-<slug>/spec.md`.
   Escribe el archivo temporal en el directorio temporal del sistema, no dentro del repo.
5. Mueve la tarjeta: `uv run scripts/tablero.py mover $ARGUMENTS "In Review"`.
6. Muestra la URL de la PR y sugiere `/revisar <número>`.
