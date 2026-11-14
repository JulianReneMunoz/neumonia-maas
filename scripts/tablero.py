# /// script
# requires-python = ">=3.13"
# dependencies = ["pyyaml"]
# ///
"""Operación diaria del Kanban: siguiente historia, mover tarjetas con WIP, métricas.

    uv run scripts/tablero.py siguiente
    uv run scripts/tablero.py historia SPEC-005
    uv run scripts/tablero.py issue SPEC-005
    uv run scripts/tablero.py mover SPEC-005 "In Progress"
    uv run scripts/tablero.py metricas
"""

from __future__ import annotations

import argparse
import statistics
import sys
from datetime import UTC, date, datetime
from typing import Any

from ghlib import (
    COLUMNAS,
    WIP_REVIEW,
    cargar_backlog,
    cargar_config,
    gh,
    gh_json,
    historia_por_id,
    spec_de_titulo,
)


def estados(items: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    """Devuelve {SPEC-NNN: item} usando el prefijo del título de la tarjeta."""
    out = {}
    for it in items:
        spec = spec_de_titulo(it.get("title", ""))
        if spec:
            out[spec] = it
    return out


def contar(items: dict[str, dict[str, Any]]) -> dict[str, int]:
    """Cuenta tarjetas por columna."""
    c = dict.fromkeys(COLUMNAS, 0)
    for it in items.values():
        c[it.get("status", "Backlog")] = c.get(it.get("status", "Backlog"), 0) + 1
    return c


def limite(columna: str, integrantes: int) -> int | None:
    """WIP de cada columna (None = sin límite)."""
    return {"In Progress": integrantes, "In Review": WIP_REVIEW}.get(columna)


def siguiente(
    historias: list[dict[str, Any]], items: dict[str, dict[str, Any]], integrantes: int
) -> tuple[dict[str, Any] | None, str]:
    """Primera historia en Backlog con dependencias en Done; explica si no hay."""
    c = contar(items)
    if c["In Progress"] >= integrantes:
        return None, f"WIP lleno en In Progress ({c['In Progress']}/{integrantes}): termina antes."
    for h in historias:
        it = items.get(h["id"])
        if not it or it.get("status", "Backlog") != "Backlog":
            continue
        pendientes = [d for d in h["depende"] if items.get(d, {}).get("status") != "Done"]
        if not pendientes:
            return h, "lista"
    return None, "No hay historias listas: faltan dependencias en Done o el backlog está vacío."


def puede_mover(destino: str, items: dict[str, dict[str, Any]], spec: str, integrantes: int) -> str | None:
    """Devuelve el motivo si mover violaría el WIP, o None si se puede."""
    tope = limite(destino, integrantes)
    if tope is None:
        return None
    actual = items[spec].get("status")
    ocupadas = sum(1 for it in items.values() if it.get("status") == destino)
    if actual != destino and ocupadas >= tope:
        return f"WIP de {destino} lleno ({ocupadas}/{tope}). Termina o fusiona algo primero."
    return None


def metricas(
    items: dict[str, dict[str, Any]],
    cerrados: dict[int, datetime],
    fusionadas: list[datetime],
    hoy: date,
    integrantes: int,
) -> dict[str, Any]:
    """Calcula WIP, work item age, cycle time y throughput semanal."""
    c = contar(items)
    edades = {}
    ciclos = []
    for spec, it in items.items():
        inicio = it.get("inicio")
        if not inicio:
            continue
        d0 = date.fromisoformat(inicio)
        if it.get("status") in {"In Progress", "In Review"}:
            edades[spec] = (hoy - d0).days
        elif it.get("status") == "Done":
            num = (it.get("content") or {}).get("number")
            if num in cerrados:
                ciclos.append((cerrados[num].date() - d0).days)
    semanas: dict[str, int] = {}
    for f in fusionadas:
        y, w, _ = f.isocalendar()
        semanas[f"{y}-S{w:02d}"] = semanas.get(f"{y}-S{w:02d}", 0) + 1
    ordenadas = sorted(semanas.items())
    return {
        "columnas": c,
        "wip": f"{c['In Progress']}/{integrantes} (In Progress), {c['In Review']}/{WIP_REVIEW} (In Review)",
        "work_item_age": edades,
        "cycle_time_dias": {
            "n": len(ciclos),
            "media": round(statistics.mean(ciclos), 1) if ciclos else None,
            "mediana": statistics.median(ciclos) if ciclos else None,
        },
        "throughput_prs_por_semana": ordenadas,
        "prs_fusionadas": len(fusionadas),
    }


def leer_items(cfg: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Lee las tarjetas del Project (gh project item-list)."""
    data = gh_json("project", "item-list", str(cfg["project_number"]), "--owner", cfg["owner"],
                   "--limit", "300", "--format", "json")  # fmt: skip
    return estados(data["items"])


def cmd_mover(cfg: dict[str, Any], spec: str, destino: str) -> None:
    """Mueve una tarjeta respetando el WIP y fija 'Inicio' al entrar a In Progress."""
    if destino not in COLUMNAS:
        sys.exit(f"Columna inválida. Usa una de: {', '.join(COLUMNAS)}")
    items = leer_items(cfg)
    spec = spec.upper()
    if spec not in items:
        sys.exit(f"{spec} no está en el tablero (¿corriste bootstrap_github.py?)")
    motivo = puede_mover(destino, items, spec, cfg["integrantes"])
    if motivo:
        sys.exit(f"✋ {motivo}")
    item, f = items[spec], cfg["fields"]
    gh("project", "item-edit", "--id", item["id"], "--project-id", cfg["project_id"],
       "--field-id", f["Status"]["id"],
       "--single-select-option-id", f["Status"]["options"][destino])  # fmt: skip
    if destino == "In Progress" and not item.get("inicio"):
        gh("project", "item-edit", "--id", item["id"], "--project-id", cfg["project_id"],
           "--field-id", f["Inicio"]["id"], "--date", date.today().isoformat())  # fmt: skip
    print(f"✅ {spec} → {destino}")


def cmd_metricas(cfg: dict[str, Any]) -> None:
    """Imprime las cuatro métricas que se preguntan en la sustentación."""
    items = leer_items(cfg)
    cerrados = {
        i["number"]: datetime.fromisoformat(i["closedAt"].replace("Z", "+00:00"))
        for i in gh_json("issue", "list", "--repo", cfg["repo"], "--state", "closed",
                         "--limit", "300", "--json", "number,closedAt") or []  # fmt: skip
    }
    fus = [
        datetime.fromisoformat(p["mergedAt"].replace("Z", "+00:00"))
        for p in gh_json("pr", "list", "--repo", cfg["repo"], "--state", "merged", "--limit", "300",
                         "--json", "mergedAt") or []  # fmt: skip
    ]
    m = metricas(items, cerrados, fus, datetime.now(UTC).date(), cfg["integrantes"])
    print("Columnas :", m["columnas"])
    print("WIP      :", m["wip"])
    print("Work item age (días):", m["work_item_age"] or "ninguna tarjeta en curso")
    ct = m["cycle_time_dias"]
    print(f"Cycle time (días)    : n={ct['n']} media={ct['media']} mediana={ct['mediana']}")
    print("Throughput (PRs/sem) :", dict(m["throughput_prs_por_semana"]) or "sin PRs aún")
    print(f"PRs fusionadas       : {m['prs_fusionadas']} / 40")


def main() -> None:
    """CLI."""
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("siguiente")
    sub.add_parser("metricas")
    for nombre in ("historia", "issue"):
        sub.add_parser(nombre).add_argument("spec")
    mv = sub.add_parser("mover")
    mv.add_argument("spec")
    mv.add_argument("columna")
    a = p.parse_args()
    backlog = cargar_backlog()
    if a.cmd == "historia":
        h = historia_por_id(backlog, a.spec)
        print(f"{h['id']} · {h['titulo']}  [{h['puntos']} pts · día {h['dia']} · {', '.join(h['labels'])}]")
        print(f"Como {h['como']}, quiero {h['quiero']} para {h['para']}")
        print(f"Depende de: {', '.join(h['depende']) or '—'} · pruebas ≥ {h['pruebas']}")
        print(f"Carpeta de la spec: specs/{h['id'][5:]}-{h['slug']}/")
        for i, c in enumerate(h["criterios"], 1):
            print(f" AC-{i}: dado {c['dado']}; cuando {c['cuando']}; entonces {c['entonces']}")
        print("Notas:", " ".join(str(h.get("notas", "")).split()))
        return
    cfg = cargar_config()
    if a.cmd == "siguiente":
        items = leer_items(cfg)
        m3 = [h for h in backlog["historias"] if h["milestone"] == "M3"]
        h, motivo = siguiente(m3, items, cfg["integrantes"])
        print(f"➡️  {h['id']} · {h['titulo']} ({h['puntos']} pts)" if h else f"⏸️  {motivo}")
    elif a.cmd == "issue":
        it = leer_items(cfg).get(a.spec.upper())
        if not it:
            sys.exit(f"{a.spec} no está en el tablero")
        print((it.get("content") or {}).get("number", ""))
    elif a.cmd == "mover":
        cmd_mover(cfg, a.spec, a.columna)
    elif a.cmd == "metricas":
        cmd_metricas(cfg)


if __name__ == "__main__":
    main()
