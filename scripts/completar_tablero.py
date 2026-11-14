# /// script
# requires-python = ">=3.13"
# dependencies = ["pyyaml"]
# ///
"""Completa el Kanban creado por bootstrap_github.py.

- Campos nuevos: «Spec» (ruta de la spec SDD) y «Bloque» (día del plan) en cada tarjeta.
- Asigna todas las historias al usuario autenticado (grupo de una persona).
- Escribe la descripción y el README del Project con las políticas del tablero
  (columnas, WIP limits, Definition of Done, flujo y métricas).
- Hace el Project público.

Uso (desde C:\\Neumonia, después de bootstrap_github.py):
    uv run scripts/completar_tablero.py --dry-run
    uv run scripts/completar_tablero.py
Es idempotente: se puede repetir.
"""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

from ghlib import cargar_backlog, cargar_config, gh, gh_json, spec_de_titulo

BLOQUES = {
    1: "1 · Sáb 14/11",
    2: "2 · Dom 15/11",
    3: "3 · Lun 16/11",
    4: "4 · Mar 17/11",
    5: "5 · Mié 18/11",
    6: "6 · M4 (después del 19/11)",
}

README = """# Kanban · neumonia-maas

Servicio de clasificación de radiografías de tórax (NORMAL / PNEUMONIA): React → FastAPI →
servicio → modelo `lxyuan/vit-xray-pneumonia-classification` (Hugging Face Hub).
Repositorio: https://github.com/{repo}

## Columnas y políticas (WIP limits)
- **Backlog** (sin límite): historia con Como/quiero/para, AC Given-When-Then y puntos
  Fibonacci. Aún no empieza.
- **In Progress** (WIP **{wip}** = nº de integrantes): spec SDD aprobada en su rama
  `feature/NNN-slug`; se implementa con TDD. Una historia por persona.
- **In Review** (WIP **2**): PR abierta hacia `develop` con plantilla, `Closes #N`, enlace a la
  spec y checks corriendo.
- **Done**: PR fusionada, checks verdes, AC cumplidos, spec Implementada y demo local.

Si una columna está llena, no se empieza otra historia: se termina o se revisa lo que está abierto.

## Regla 1:1
Cada tarjeta = 1 issue (`SPEC-NNN`) = 1 spec en `specs/NNN-slug/` (spec.md, plan.md, tasks.md) = 1 PR.
La spec se escribe y aprueba **antes** del código.

## Flujo
Backlog → spec SDD (spec + plan + tasks) → rama `feature/*` → In Progress → PR con plantilla →
In Review → revisión + CI (ruff + pytest) → merge a `develop` → Done.

## Definition of Done
Spec SDD · código · pruebas · documentación · PR revisada y fusionada con checks verdes · demo local.

## Campos
**Puntos** (Fibonacci 1, 2, 3, 5, 8; una estimación por historia) · **Inicio** (fecha de entrada a
In Progress) · **Spec** (ruta) · **Bloque** (día del plan) · labels por capa · milestone M3/M4.

## Métricas
- **WIP:** tarjetas en In Progress + In Review frente a su límite.
- **Throughput:** PRs/historias cerradas por semana (Insights).
- **Work item age:** días desde *Inicio* para tarjetas aún abiertas.
- **Cycle time:** días entre *Inicio* y el merge.
Se calculan con `uv run scripts/tablero.py metricas`.
"""


def asegurar_campos(numero: str, owner: str, dry: bool) -> dict[str, dict]:
    """Crea los campos Spec y Bloque si no existen y devuelve el mapa de campos."""
    actuales = {} if dry else {
        c["name"]: c
        for c in gh_json("project", "field-list", numero, "--owner", owner, "--format", "json")[
            "fields"
        ]
    }
    if "Spec" not in actuales:
        gh("project", "field-create", numero, "--owner", owner, "--name", "Spec",
           "--data-type", "TEXT", dry_run=dry)  # fmt: skip
    if "Bloque" not in actuales:
        gh("project", "field-create", numero, "--owner", owner, "--name", "Bloque",
           "--data-type", "SINGLE_SELECT",
           "--single-select-options", ",".join(BLOQUES.values()), dry_run=dry)  # fmt: skip
    if dry:
        return {}
    campos = gh_json("project", "field-list", numero, "--owner", owner, "--format", "json")
    return {
        c["name"]: {"id": c["id"], "options": {o["name"]: o["id"] for o in c.get("options", [])}}
        for c in campos["fields"]
    }


def main() -> None:
    """Orquesta la configuración."""
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    p.add_argument("--dry-run", action="store_true")
    a = p.parse_args()
    cfg = cargar_config()
    backlog = {h["id"]: h for h in cargar_backlog()["historias"]}
    numero, owner, pid, repo = str(cfg["project_number"]), cfg["owner"], cfg["project_id"], cfg["repo"]

    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8") as f:
        f.write(README.format(repo=repo, wip=cfg["integrantes"]))
        ruta_readme = f.name
    gh("project", "edit", numero, "--owner", owner, "--visibility", "PUBLIC",
       "--description", "Kanban del M3: Backlog → In Progress (WIP 1) → In Review (WIP 2) → Done. "
       "Una tarjeta = una historia = una spec SDD = una PR.",
       "--readme", Path(ruta_readme).read_text(encoding="utf-8"), dry_run=a.dry_run)  # fmt: skip
    Path(ruta_readme).unlink(missing_ok=True)

    campos = asegurar_campos(numero, owner, a.dry_run)
    if a.dry_run:
        print("DRY-RUN: luego se completan Spec, Bloque y responsable en las 45 tarjetas.")
        return
    items = gh_json("project", "item-list", numero, "--owner", owner, "--limit", "300",
                    "--format", "json")["items"]  # fmt: skip
    for it in items:
        spec = spec_de_titulo(it.get("title", ""))
        if not spec or spec not in backlog:
            continue
        h = backlog[spec]
        ruta = f"specs/{spec[5:]}-{h['slug']}/"
        gh("project", "item-edit", "--id", it["id"], "--project-id", pid,
           "--field-id", campos["Spec"]["id"], "--text", ruta)  # fmt: skip
        gh("project", "item-edit", "--id", it["id"], "--project-id", pid,
           "--field-id", campos["Bloque"]["id"],
           "--single-select-option-id", campos["Bloque"]["options"][BLOQUES[h["dia"]]])  # fmt: skip
        numero_issue = (it.get("content") or {}).get("number")
        if numero_issue:
            gh("issue", "edit", str(numero_issue), "--repo", repo, "--add-assignee", "@me")
        print(f"✔ {spec}  {ruta}  {BLOQUES[h['dia']]}")
    print(f"\nListo. Project público: https://github.com/users/{owner}/projects/{numero}")
    print("Falta lo que solo se hace en la web: vista Board, límites de columna y campos visibles.")


if __name__ == "__main__":
    main()
