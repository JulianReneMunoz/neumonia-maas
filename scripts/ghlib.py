# /// script
# requires-python = ">=3.13"
# dependencies = ["pyyaml"]
# ///
"""Utilidades compartidas por bootstrap_github.py y tablero.py (solo gh + stdlib + PyYAML)."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import yaml

RAIZ = Path(__file__).resolve().parent.parent
BACKLOG = RAIZ / "docs" / "backlog.yaml"
CONFIG_TABLERO = RAIZ / "docs" / "tablero.json"
COLUMNAS = ["Backlog", "In Progress", "In Review", "Done"]
COLUMNA_DESCRIPCION = {
    "Backlog": "Sin WIP. Todo lo que aún no empieza.",
    "In Progress": "WIP = nº de integrantes. Una historia por persona; si está lleno, no se empieza otra.",
    "In Review": "WIP = 2. PR abierta, reviewer asignado, checks corriendo.",
    "Done": "Mergeada, tests verdes, AC cumplidos, spec implementada y demo local.",
}
COLUMNA_COLOR = {"Backlog": "GRAY", "In Progress": "YELLOW", "In Review": "PURPLE", "Done": "GREEN"}
WIP_REVIEW = 2


def cargar_backlog() -> dict[str, Any]:
    """Lee docs/backlog.yaml."""
    return yaml.safe_load(BACKLOG.read_text(encoding="utf-8"))


def historia_por_id(backlog: dict[str, Any], spec_id: str) -> dict[str, Any]:
    """Busca una historia por su ID (SPEC-NNN); termina el programa si no existe."""
    for h in backlog["historias"]:
        if h["id"] == spec_id.upper():
            return h
    sys.exit(f"No existe {spec_id} en docs/backlog.yaml")


def gh(*args: str, dry_run: bool = False, check: bool = True) -> str:
    """Ejecuta `gh` y devuelve stdout; con dry_run solo imprime el comando."""
    if dry_run:
        print("DRY-RUN  gh " + " ".join(a if " " not in a else repr(a) for a in args))
        return ""
    res = subprocess.run(
        ["gh", *args], capture_output=True, text=True, encoding="utf-8", check=False
    )
    if check and res.returncode != 0:
        sys.exit(f"gh {' '.join(args[:3])} falló:\n{res.stderr.strip()}")
    return res.stdout


def gh_json(*args: str) -> Any:
    """Ejecuta `gh ... ` y parsea la salida JSON."""
    salida = gh(*args)
    return json.loads(salida) if salida.strip() else None


def cargar_config() -> dict[str, Any]:
    """Lee docs/tablero.json (lo crea bootstrap_github.py)."""
    if not CONFIG_TABLERO.exists():
        sys.exit("Falta docs/tablero.json: ejecuta primero scripts/bootstrap_github.py")
    return json.loads(CONFIG_TABLERO.read_text(encoding="utf-8"))


def spec_de_titulo(titulo: str) -> str | None:
    """Extrae 'SPEC-NNN' del inicio de un título de issue/tarjeta."""
    if titulo.upper().startswith("SPEC-") and len(titulo) >= 8 and titulo[5:8].isdigit():
        return titulo[:8].upper()
    return None


def cuerpo_issue(h: dict[str, Any]) -> str:
    """Genera el cuerpo Markdown del issue a partir de la historia del backlog."""
    ac = []
    for i, c in enumerate(h["criterios"], start=1):
        ac.append(
            f"**AC-{i}**\n- **Dado** {c['dado']}\n- **Cuando** {c['cuando']}\n"
            f"- **Entonces** {c['entonces']}"
        )
    depende = ", ".join(h["depende"]) or "ninguna"
    ruta = f"specs/{h['id'][5:]}-{h['slug']}/"
    return (
        f"## Historia\n**Como** {h['como']}, **quiero** {h['quiero']} **para** {h['para']}.\n\n"
        f"## Criterios de aceptación\n\n" + "\n\n".join(ac) + "\n\n"
        f"## Estimación\n{h['puntos']} puntos (Fibonacci) · piso de pruebas: {h['pruebas']}\n\n"
        f"## Spec SDD\n`{ruta}` (spec.md, plan.md, tasks.md) — se escribe **antes** del código.\n\n"
        f"## Dependencias\n{depende}\n\n"
        f"## Notas\n{' '.join(str(h.get('notas', '')).split())}\n\n"
        f"## Definition of Done\n- [ ] Spec SDD aprobada\n- [ ] Código\n- [ ] Pruebas\n"
        f"- [ ] Documentación\n- [ ] PR aprobada y fusionada con checks verdes\n"
        f"- [ ] Demo local\n"
    )
