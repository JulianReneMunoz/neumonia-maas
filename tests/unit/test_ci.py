import re
from pathlib import Path
from typing import Any, Final

import pytest
import yaml

RUTA_WORKFLOW: Final = Path(".github") / "workflows" / "ci.yml"
RAMAS_LARGAS: Final = {"develop", "main"}


@pytest.fixture
def workflow_ci(raiz_repo: Path) -> dict[Any, Any]:
    """Workflow de CI parseado con yaml.safe_load."""
    texto = (raiz_repo / RUTA_WORKFLOW).read_text(encoding="utf-8")
    return yaml.safe_load(texto)


def _pasos(workflow: dict[Any, Any]) -> list[dict[str, Any]]:
    """Pasos del job `ci`, en orden."""
    return workflow["jobs"]["ci"]["steps"]


def _comandos_run(workflow: dict[Any, Any]) -> list[str]:
    """Lista ordenada de los `run:` del job `ci`."""
    return [paso["run"].strip() for paso in _pasos(workflow) if "run" in paso]


def _disparadores(workflow: dict[Any, Any]) -> dict[str, Any]:
    """Sección `on:` del workflow.

    PyYAML implementa YAML 1.1, donde `on` es un booleano: la clave llega como `True`.
    GitHub Actions la interpreta como texto, así que se aceptan las dos formas.
    """
    return workflow.get("on", workflow.get(True))


def test_workflow_parsea_y_tiene_unico_job_ci(workflow_ci: dict[Any, Any]) -> None:
    # Arrange
    jobs = workflow_ci["jobs"]

    # Act
    ids = list(jobs)

    # Assert
    assert ids == ["ci"], "la protección de ramas exige exactamente el check `ci`"


def test_disparadores_pr_y_push_a_develop_y_main(workflow_ci: dict[Any, Any]) -> None:
    # Arrange
    disparadores = _disparadores(workflow_ci)

    # Act
    ramas_pr = set(disparadores["pull_request"]["branches"])
    ramas_push = set(disparadores["push"]["branches"])

    # Assert
    assert RAMAS_LARGAS <= ramas_pr
    assert RAMAS_LARGAS <= ramas_push


def test_setup_uv_con_cache_y_python_igual_a_python_version(
    workflow_ci: dict[Any, Any], raiz_repo: Path
) -> None:
    # Arrange
    python_fijado = (raiz_repo / ".python-version").read_text(encoding="utf-8").strip()

    # Act
    setup_uv = [
        p for p in _pasos(workflow_ci) if p.get("uses", "").startswith("astral-sh/setup-uv@")
    ]

    # Assert
    assert len(setup_uv) == 1
    opciones = setup_uv[0]["with"]
    assert opciones["enable-cache"] is True
    assert opciones["cache-dependency-glob"] == "uv.lock"
    assert str(opciones["python-version"]) == python_fijado


def test_pasos_en_orden_sync_locked_ruff_format_pytest(workflow_ci: dict[Any, Any]) -> None:
    # Arrange
    esperados = [
        "uv sync --locked",
        "uv run ruff check .",
        "uv run ruff format --check .",
        "uv run pytest",
    ]

    # Act
    comandos = _comandos_run(workflow_ci)

    # Assert
    assert [c for c in comandos if c in esperados] == esperados


def test_ningun_paso_ignora_fallos(workflow_ci: dict[Any, Any]) -> None:
    # Arrange
    job = workflow_ci["jobs"]["ci"]

    # Act
    ignoran = [
        paso.get("name", paso.get("uses", paso.get("run")))
        for paso in job["steps"]
        if paso.get("continue-on-error")
    ]

    # Assert
    assert not job.get("continue-on-error"), "el job no puede ignorar fallos"
    assert ignoran == [], f"pasos con continue-on-error: {ignoran}"


def test_sin_pip_ni_setup_python(workflow_ci: dict[Any, Any]) -> None:
    # Arrange
    pasos = _pasos(workflow_ci)

    # Act
    usa_setup_python = [
        p["uses"] for p in pasos if p.get("uses", "").startswith("actions/setup-python")
    ]
    usa_pip = [c for c in _comandos_run(workflow_ci) if re.search(r"\bpip\b", c)]

    # Assert
    assert usa_setup_python == []
    assert usa_pip == []


def test_permisos_minimos_y_sin_matrix(workflow_ci: dict[Any, Any]) -> None:
    # Arrange
    job = workflow_ci["jobs"]["ci"]

    # Act
    permisos = workflow_ci.get("permissions")

    # Assert
    assert permisos == {"contents": "read"}
    assert "strategy" not in job, "una matriz cambiaría el nombre del check (ci (3.13))"
    assert "name" not in job, "un name cambiaría el nombre del check"
