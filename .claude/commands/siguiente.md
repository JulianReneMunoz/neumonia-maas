---
description: Muestra la siguiente historia del backlog lista para empezar (dependencias cumplidas y WIP libre)
---
1. Ejecuta `uv run scripts/tablero.py siguiente` y muestra la salida.
2. Si hay una historia lista, resume en 3 líneas qué pide (historia y AC) y propone:
   `/spec SPEC-NNN`.
3. Si el WIP de *In Progress* está lleno, dilo y muestra qué historia está en curso
   (`uv run scripts/tablero.py metricas`). No propongas empezar otra.
4. Si hay PRs abiertas esperando revisión o merge, recuérdalas primero
   (`gh pr list --state open`): terminar va antes que empezar.
