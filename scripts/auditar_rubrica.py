# /// script
# requires-python = ">=3.13"
# dependencies = ["pyyaml"]
# ///
"""Audita que cada ítem del checklist del anuncio 007 tenga historias del backlog que lo cubran."""

from __future__ import annotations

import sys
from pathlib import Path

import yaml

RAIZ = Path(__file__).resolve().parent.parent

# ítem del checklist (anuncio 007, sección 11) -> historias que lo implementan o evidencian
COBERTURA: dict[str, list[str]] = {
    "A1 Frontend separado (React)": ["SPEC-018"],
    "A2 Sin Streamlit/Gradio/Dash": ["SPEC-018"],
    "A3 Carga + estados loading/success/error + resultado": ["SPEC-020", "SPEC-021", "SPEC-022"],
    "A4 Petición visible en Network (HTTP/JSON)": ["SPEC-019", "SPEC-012"],
    "A5 App sin errores, modelo en tiempo real": ["SPEC-012", "SPEC-023", "SPEC-032"],
    "B1 FastAPI + contrato OpenAPI": ["SPEC-010", "SPEC-011", "SPEC-034"],
    "B2 3 capas": ["SPEC-005", "SPEC-009", "SPEC-012"],
    "B3 Schemas Pydantic y errores 400/422/500": ["SPEC-011", "SPEC-013"],
    "B4 /health y carga única (lifespan)": ["SPEC-010"],
    "B5 Sin lógica de modelo en la API": ["SPEC-009", "SPEC-012"],
    "C1 Servidor MLflow y UI en vivo": ["SPEC-027"],
    "C2 3 runs comparables": ["SPEC-029", "SPEC-030"],
    "C3 Parámetros (modelo@rev, preproc, umbral, dataset, backend)": ["SPEC-029", "SPEC-028"],
    "C4 Métricas (acc/F1/AUC + latencia + throughput)": ["SPEC-029"],
    "C5 Artefactos (modelo, predicciones, gráficos, reporte)": ["SPEC-029", "SPEC-031"],
    "C6 Tags y Model Registry consistentes": ["SPEC-027", "SPEC-031"],
    "D1 GitHub Projects 4 columnas": ["SPEC-003"],
    "D2 WIP limits escritos": ["SPEC-003"],
    "D3 Historias con AC y Fibonacci 1:1": ["SPEC-003"],
    "D4 Historia apunta a su spec": ["SPEC-003"],
    "D5 PR con Closes #N, spec y tarjeta a Done tras merge": ["SPEC-003"],
    "D6 Métricas del tablero explicadas": ["SPEC-003", "SPEC-040"],
    "E1 40 PRs fusionadas con issue, revisión y checks": ["SPEC-002"],
    "E2 40 specs con spec/plan/tasks": ["SPEC-001"],
    "E3 Gitflow, sin commits directos": ["SPEC-002", "SPEC-036"],
    "E4 Conventional Commits y plantilla de PR": ["SPEC-003"],
    "E5 >=120 pruebas pytest AAA sin red ni GPU": ["SPEC-017", "SPEC-032", "SPEC-033"],
    "E6 Python 3.13 + uv, cero pip": ["SPEC-001"],
    "E7 ruff limpio, type hints, docstrings, cero warnings": ["SPEC-001", "SPEC-040"],
    "E8 CI GitHub Actions y Dockerfile CPU": ["SPEC-002", "SPEC-035"],
    "F1 README con badges y secciones": ["SPEC-037"],
    "F2 LICENSE MIT y docs/": ["SPEC-001"],
    "F3 Diagrama Archify enlazado": ["SPEC-039"],
    "F4 Model Card en docs/model-card.md": ["SPEC-038"],
    "F5 specs/ enlazada desde el README": ["SPEC-037"],
    "F6 .gitignore (pesos, .env, .venv, data/raw, ipynb)": ["SPEC-001", "SPEC-036"],
}


def main() -> int:
    """Verifica IDs, pruebas totales y conteos; devuelve 1 si algo falla."""
    d = yaml.safe_load((RAIZ / "docs" / "backlog.yaml").read_text(encoding="utf-8"))
    m3 = {h["id"]: h for h in d["historias"] if h["milestone"] == "M3"}
    fallos = []
    for item, ids in COBERTURA.items():
        malos = [i for i in ids if i not in m3]
        if malos or not ids:
            fallos.append(f"{item}: historias inexistentes {malos}")
    total_pruebas = sum(h["pruebas"] for h in m3.values())
    if len(m3) < 40:
        fallos.append(f"Solo {len(m3)} historias M3 (<40)")
    if total_pruebas < 120:
        fallos.append(f"Piso de pruebas {total_pruebas} (<120)")
    for h in m3.values():
        if h["puntos"] not in (1, 2, 3, 5, 8) or not h["criterios"]:
            fallos.append(f"{h['id']}: puntos o AC inválidos")
    print(f"Ítems cubiertos: {len(COBERTURA) - len(fallos)}/{len(COBERTURA)} · "
          f"historias M3: {len(m3)} · piso de pruebas: {total_pruebas}")
    for f in fallos:
        print("❌", f)
    return 1 if fallos else 0


if __name__ == "__main__":
    sys.exit(main())
