import tomllib
from pathlib import Path
from typing import Any

import pytest


@pytest.fixture
def raiz_repo() -> Path:
    """Raíz del repositorio (carpeta que contiene pyproject.toml)."""
    return Path(__file__).resolve().parents[1]


@pytest.fixture
def pyproject(raiz_repo: Path) -> dict[str, Any]:
    """Contenido de pyproject.toml ya parseado."""
    with (raiz_repo / "pyproject.toml").open("rb") as archivo:
        return tomllib.load(archivo)
