# /// script
# requires-python = ">=3.13"
# dependencies = ["pyyaml"]
# ///
"""Crea en GitHub todo lo que el Kanban necesita a partir de docs/backlog.yaml.

Crea: labels, milestones, el Project (4 columnas con WIP en la descripción, campos Puntos
e Inicio), un issue por historia y sus tarjetas en Backlog con los puntos asignados.

Uso (desde la raíz del repo, con `gh auth login` hecho):
    uv run scripts/bootstrap_github.py --repo USUARIO/neumonia-maas --integrantes 1 --dry-run
    uv run scripts/bootstrap_github.py --repo USUARIO/neumonia-maas --integrantes 1

Es reanudable: si un issue con el mismo título ya existe, no lo duplica.
"""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

from ghlib import (
    COLUMNA_COLOR,
    COLUMNA_DESCRIPCION,
    COLUMNAS,
    CONFIG_TABLERO,
    cargar_backlog,
    cuerpo_issue,
    gh,
    gh_json,
)

LABELS = {
    "backend": "0e8a16",
    "frontend": "1d76db",
    "inferencia": "5319e7",
    "mlflow": "0052cc",
    "qa": "fbca04",
    "docs": "c5def5",
    "infra": "bfd4f2",
    "kanban": "d4c5f9",
    "bug": "d73a4a",
    "m4": "f9d0c4",
}


def crear_labels(repo: str, dry: bool) -> None:
    """Crea los labels por capa (idempotente con --force)."""
    for nombre, color in LABELS.items():
        gh("label", "create", nombre, "--repo", repo, "--color", color, "--force", dry_run=dry)


def crear_milestones(repo: str, hitos: dict[str, str], dry: bool) -> None:
    """Crea los milestones si no existen."""
    existentes = set()
    if not dry:
        existentes = {
            m["title"] for m in gh_json("api", f"repos/{repo}/milestones?state=all") or []
        }
    for titulo, descripcion in hitos.items():
        if titulo in existentes:
            continue
        gh(
            "api", f"repos/{repo}/milestones", "-f", f"title={titulo}",
            "-f", f"description={descripcion}", dry_run=dry,
        )  # fmt: skip


def crear_project(owner: str, repo: str, titulo: str, dry: bool) -> dict:
    """Crea el Project, lo enlaza al repo y deja columnas y campos listos."""
    if dry:
        gh(
            "project",
            "create",
            "--owner",
            owner,
            "--title",
            titulo,
            "--format",
            "json",
            dry_run=True,
        )
        gh("project", "link", "<N>", "--owner", owner, "--repo", repo, dry_run=True)
        return {"number": 0, "id": "DRY", "fields": {}}
    proyecto = gh_json("project", "create", "--owner", owner, "--title", titulo, "--format", "json")
    numero, pid = str(proyecto["number"]), proyecto["id"]
    gh("project", "link", numero, "--owner", owner, "--repo", repo)
    for nombre, tipo in (("Puntos", "NUMBER"), ("Inicio", "DATE")):
        gh("project", "field-create", numero, "--owner", owner, "--name", nombre,
           "--data-type", tipo)  # fmt: skip
    campos = gh_json("project", "field-list", numero, "--owner", owner, "--format", "json")
    status = next(c for c in campos["fields"] if c["name"] == "Status")
    opciones = ", ".join(
        '{name: "'
        + c
        + '", color: '
        + COLUMNA_COLOR[c]
        + ', description: "'
        + COLUMNA_DESCRIPCION[c].replace('"', "'")
        + '"}'
        for c in COLUMNAS
    )
    mutacion = (
        'mutation { updateProjectV2Field(input: {fieldId: "' + status["id"] + '", '
        "singleSelectOptions: [" + opciones + "]}) "
        "{ projectV2Field { ... on ProjectV2SingleSelectField { id } } } }"
    )
    gh("api", "graphql", "-f", f"query={mutacion}")
    campos = gh_json("project", "field-list", numero, "--owner", owner, "--format", "json")
    mapa = {
        c["name"]: {"id": c["id"], "options": {o["name"]: o["id"] for o in c.get("options", [])}}
        for c in campos["fields"]
    }
    faltan = [c for c in COLUMNAS if c not in mapa["Status"]["options"]]
    if faltan:
        raise SystemExit(
            f"No se pudieron crear las columnas {faltan}; créalas a mano en el Project."
        )
    return {"number": int(numero), "id": pid, "fields": mapa}


def crear_issues(repo: str, owner: str, proyecto: dict, historias: list, dry: bool) -> None:
    """Crea un issue por historia y su tarjeta en Backlog con los puntos."""
    existentes: dict[str, str] = {}
    if not dry:
        for i in gh_json("issue", "list", "--repo", repo, "--state", "all", "--limit", "300",
                         "--json", "title,url") or []:  # fmt: skip
            existentes[i["title"]] = i["url"]
    num, pid, campos = str(proyecto["number"]), proyecto["id"], proyecto["fields"]
    for h in historias:
        titulo = f"{h['id']} · {h['titulo']}"
        if titulo in existentes:
            url = existentes[titulo]
            print(f"= ya existe: {titulo}")
        else:
            with tempfile.NamedTemporaryFile(
                "w", suffix=".md", delete=False, encoding="utf-8"
            ) as f:
                f.write(cuerpo_issue(h))
                cuerpo = f.name
            args = ["issue", "create", "--repo", repo, "--title", titulo, "--body-file", cuerpo,
                    "--milestone", h["milestone"]]  # fmt: skip
            for etiqueta in h["labels"]:
                args += ["--label", etiqueta]
            url = gh(*args, dry_run=dry).strip()
            Path(cuerpo).unlink(missing_ok=True)
            print(f"+ {titulo}")
        if dry:
            continue
        item = json.loads(
            gh("project", "item-add", num, "--owner", owner, "--url", url, "--format", "json")
        )
        gh("project", "item-edit", "--id", item["id"], "--project-id", pid,
           "--field-id", campos["Status"]["id"],
           "--single-select-option-id", campos["Status"]["options"]["Backlog"])  # fmt: skip
        gh("project", "item-edit", "--id", item["id"], "--project-id", pid,
           "--field-id", campos["Puntos"]["id"], "--number", str(h["puntos"]))  # fmt: skip


def main() -> None:
    """Orquesta la creación completa."""
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    p.add_argument("--repo", required=True, help="USUARIO/repositorio")
    p.add_argument("--owner", help="dueño del Project (por defecto, el del repo)")
    p.add_argument("--integrantes", type=int, default=1, help="WIP de In Progress")
    p.add_argument("--solo-m3", action="store_true", help="no crear las historias del M4")
    p.add_argument("--dry-run", action="store_true", help="solo imprimir los comandos")
    a = p.parse_args()
    owner = a.owner or a.repo.split("/")[0]
    backlog = cargar_backlog()
    historias = [h for h in backlog["historias"] if not (a.solo_m3 and h["milestone"] != "M3")]
    crear_labels(a.repo, a.dry_run)
    crear_milestones(a.repo, backlog["proyecto"]["milestones"], a.dry_run)
    proyecto = crear_project(owner, a.repo, f"Kanban · {backlog['proyecto']['nombre']}", a.dry_run)
    crear_issues(a.repo, owner, proyecto, historias, a.dry_run)
    if not a.dry_run:
        config = {"repo": a.repo, "owner": owner, "project_number": proyecto["number"],
                  "project_id": proyecto["id"], "integrantes": a.integrantes,
                  "fields": proyecto["fields"]}  # fmt: skip
        CONFIG_TABLERO.write_text(json.dumps(config, indent=2), encoding="utf-8")
        print(f"\nListo. Config en {CONFIG_TABLERO}. Abre el Project y cambia la vista a Board.")
        print("Haz el Project público (Settings → Visibility) o invita al profesor.")


if __name__ == "__main__":
    main()
