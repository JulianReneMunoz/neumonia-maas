import tomllib
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest


@pytest.fixture(autouse=True)
def _cache_settings_limpia() -> Iterator[None]:
    """Vacía la caché de get_settings() antes y después de cada prueba.

    Así ninguna prueba (de esta ni de futuras historias) hereda la configuración de otra.
    """
    from neumonia.config import get_settings

    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


@pytest.fixture
def raiz_repo() -> Path:
    """Raíz del repositorio (carpeta que contiene pyproject.toml)."""
    return Path(__file__).resolve().parents[1]


@pytest.fixture
def pyproject(raiz_repo: Path) -> dict[str, Any]:
    """Contenido de pyproject.toml ya parseado."""
    with (raiz_repo / "pyproject.toml").open("rb") as archivo:
        return tomllib.load(archivo)
