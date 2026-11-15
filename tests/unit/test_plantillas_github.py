import json
import re
from pathlib import Path
from typing import Any, Final

import pytest
import yaml

PLANTILLAS: Final = Path(".github") / "ISSUE_TEMPLATE"
FIBONACCI: Final = ["1", "2", "3", "5", "8"]
SECCIONES_CONTRIBUTING: Final = [
    "## Flujo de una historia",
    "## Columnas y WIP limits",
    "## Definition of Done",
    "## Ramas (Gitflow)",
    "## Commits (Conventional Commits)",
    "## Crear una historia y abrir la PR",
    "## Reglas no negociables",
]
FLUJO: Final = "Backlog → spec → rama → PR → review → merge → Done"
DOD: Final = [
    "Spec SDD aprobada",
    "código",
    "pruebas",
    "documentación",
    "PR revisada y fusionada con checks verdes",
    "demo local",
]
ENLACES_CONTRIBUTING: Final = [
    ".github/PULL_REQUEST_TEMPLATE.md",
    "CLAUDE.md",
    "docs/backlog.yaml",
    "docs/plantillas-sdd/",
]
COMANDOS: Final = ["/siguiente", "/spec", "/implementar", "/pr", "/revisar", "/fusionar"]


def _cargar_yaml(raiz: Path, nombre: str) -> dict[str, Any]:
    """Parsea un archivo de .github/ISSUE_TEMPLATE con yaml.safe_load."""
    return yaml.safe_load((raiz / PLANTILLAS / nombre).read_text(encoding="utf-8"))


def _campos_por_id(formulario: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Campos del issue form indexados por su id (los bloques markdown no tienen id)."""
    return {campo["id"]: campo for campo in formulario["body"] if "id" in campo}


def _requerido(campo: dict[str, Any]) -> bool:
    return bool(campo.get("validations", {}).get("required", False))


@pytest.fixture
def historia(raiz_repo: Path) -> dict[str, Any]:
    """Issue form «Historia de usuario»."""
    return _cargar_yaml(raiz_repo, "historia.yml")


def test_historia_exige_historia_ac_puntos_y_spec(historia: dict[str, Any]) -> None:
    # Arrange
    tipos_esperados = {
        "historia": "textarea",
        "ac": "textarea",
        "puntos": "dropdown",
        "spec": "input",
    }

    # Act
    campos = _campos_por_id(historia)
    primer_bloque = historia["body"][0]

    # Assert
    assert historia["name"] == "Historia de usuario"
    assert historia["title"].startswith("SPEC-NNN")
    for id_campo, tipo in tipos_esperados.items():
        assert campos[id_campo]["type"] == tipo
        assert _requerido(campos[id_campo]), f"`{id_campo}` debe ser obligatorio"
    assert not _requerido(campos["dependencias"]), "`dependencias` debe ser opcional"
    assert primer_bloque["type"] == "markdown"
    assert "CONTRIBUTING.md" in primer_bloque["attributes"]["value"]


def test_historia_puntos_solo_fibonacci(historia: dict[str, Any]) -> None:
    # Arrange
    puntos = _campos_por_id(historia)["puntos"]

    # Act
    opciones = [str(opcion) for opcion in puntos["attributes"]["options"]]

    # Assert
    assert opciones == FIBONACCI
    assert not puntos["attributes"].get("multiple", False), "una sola estimación"
    assert _requerido(puntos)


def test_bug_y_config_sin_issues_en_blanco(raiz_repo: Path) -> None:
    # Arrange
    bug = _cargar_yaml(raiz_repo, "bug.yml")
    config = _cargar_yaml(raiz_repo, "config.yml")

    # Act
    campos_bug = _campos_por_id(bug)
    enlaces = [enlace["url"] for enlace in config.get("contact_links", [])]

    # Assert
    assert "bug" in bug["labels"]
    assert _requerido(campos_bug["pasos"])
    assert _requerido(campos_bug["esperado"])
    assert not _requerido(campos_bug["spec"])
    assert config["blank_issues_enabled"] is False
    assert any(url.endswith("/CONTRIBUTING.md") for url in enlaces)


def _wip_en_tabla(texto: str, columna: str) -> int:
    """Número en negrita de la fila `| <columna> | **N** …` de la tabla de WIP."""
    coincidencia = re.search(rf"^\|\s*{re.escape(columna)}\s*\|\s*\*\*(\d+)\*\*", texto, re.M)
    assert coincidencia, f"no hay fila de WIP para {columna}"
    return int(coincidencia.group(1))


def test_contributing_tiene_flujo_wip_y_dod_coherentes(raiz_repo: Path) -> None:
    # Arrange
    guia = (raiz_repo / "CONTRIBUTING.md").read_text(encoding="utf-8")
    readme = (raiz_repo / "README.md").read_text(encoding="utf-8")
    integrantes = json.loads((raiz_repo / "docs" / "tablero.json").read_text(encoding="utf-8"))[
        "integrantes"
    ]
    # ghlib.py se lee como texto: trae su propia cabecera PEP 723 y no se importa.
    ghlib = (raiz_repo / "scripts" / "ghlib.py").read_text(encoding="utf-8")
    wip_review = int(re.search(r"^WIP_REVIEW\s*=\s*(\d+)", ghlib, re.M).group(1))
    seccion_dod = guia.split("## Definition of Done", 1)[-1].split("\n## ", 1)[0]

    # Act
    faltan_secciones = [s for s in SECCIONES_CONTRIBUTING if s not in guia]
    faltan_comandos = [c for c in COMANDOS if f"`{c}" not in guia]
    faltan_dod = [d for d in DOD if d not in seccion_dod]
    faltan_enlaces = [e for e in ENLACES_CONTRIBUTING if e not in guia]

    # Assert
    assert faltan_secciones == []
    assert FLUJO in guia
    assert faltan_comandos == []
    assert _wip_en_tabla(guia, "In Progress") == integrantes
    assert _wip_en_tabla(guia, "In Review") == wip_review
    assert faltan_dod == []
    assert faltan_enlaces == []
    assert "](CONTRIBUTING.md)" in readme


def test_contributing_columna_de_spec_coincide_con_el_comando(raiz_repo: Path) -> None:
    # Arrange
    guia = (raiz_repo / "CONTRIBUTING.md").read_text(encoding="utf-8")
    comando_spec = (raiz_repo / ".claude" / "commands" / "spec.md").read_text(encoding="utf-8")
    movida = re.search(r'tablero\.py mover \$ARGUMENTS "([^"]+)"', comando_spec)

    # Act
    fila_spec = next(linea for linea in guia.splitlines() if linea.startswith("| 2. Especificar"))
    columna_guia = fila_spec.rstrip(" |").rsplit("|", 1)[-1]

    # Assert
    # La guía debe describir lo que hace `/spec` de verdad (ahí empieza a contar el cycle time).
    assert movida, "el comando /spec ya no mueve la tarjeta: revisar la guía"
    assert columna_guia.strip().startswith(movida.group(1))
