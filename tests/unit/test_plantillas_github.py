from pathlib import Path
from typing import Any, Final

import pytest
import yaml

PLANTILLAS: Final = Path(".github") / "ISSUE_TEMPLATE"
FIBONACCI: Final = ["1", "2", "3", "5", "8"]


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
