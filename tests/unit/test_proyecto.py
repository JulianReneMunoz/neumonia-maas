import os
import re
from pathlib import Path
from typing import Any

# Carpetas que no son código del repo (entornos, cachés, datos ignorados por Git).
CARPETAS_IGNORADAS = {
    ".git",
    ".venv",
    "node_modules",
    "data",
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache",
    "mlruns",
    "mlartifacts",
}


def _nombre_paquete(requisito: str) -> str:
    """Extrae el nombre de un requisito PEP 508 (p. ej. 'ruff>=0.14' -> 'ruff')."""
    return re.split(r"[<>=!~\[; ]", requisito, maxsplit=1)[0].lower()


def _archivos_del_repo(raiz: Path) -> list[Path]:
    archivos: list[Path] = []
    for carpeta, subcarpetas, nombres in os.walk(raiz):
        subcarpetas[:] = [c for c in subcarpetas if c not in CARPETAS_IGNORADAS]
        archivos.extend(Path(carpeta) / n for n in nombres)
    return archivos


def test_python_fijado_a_313(raiz_repo: Path, pyproject: dict[str, Any]) -> None:
    # Arrange
    archivo_version = raiz_repo / ".python-version"

    # Act
    version_fijada = archivo_version.read_text(encoding="utf-8").strip()
    requiere = pyproject["project"]["requires-python"]

    # Assert
    assert version_fijada == "3.13"
    assert requiere == ">=3.13"


def test_build_backend_y_grupo_dev(pyproject: dict[str, Any]) -> None:
    # Arrange
    esperadas = {"pytest", "pytest-cov", "ruff"}

    # Act
    backend = pyproject["build-system"]["build-backend"]
    grupo_dev = {_nombre_paquete(r) for r in pyproject["dependency-groups"]["dev"]}

    # Assert
    assert backend == "uv_build"
    assert esperadas <= grupo_dev


def test_ruff_reglas_y_convencion_google(pyproject: dict[str, Any]) -> None:
    # Arrange
    reglas_esperadas = {"E", "F", "I", "UP", "B", "D", "ANN"}
    ruff = pyproject["tool"]["ruff"]

    # Act
    reglas = set(ruff["lint"]["select"])
    convencion = ruff["lint"]["pydocstyle"]["convention"]

    # Assert
    assert reglas_esperadas <= reglas
    assert convencion == "google"
    assert ruff["target-version"] == "py313"


def test_pytest_testpaths_quiet_y_warnings_error(pyproject: dict[str, Any]) -> None:
    # Arrange
    opciones = pyproject["tool"]["pytest"]["ini_options"]

    # Act
    testpaths = opciones["testpaths"]
    addopts = opciones["addopts"]
    filtros = opciones["filterwarnings"]

    # Assert
    assert testpaths == ["tests"]
    assert "-q" in addopts
    assert "error" in filtros


def test_makefile_check_corre_ruff_y_pytest(raiz_repo: Path) -> None:
    # Arrange
    texto = (raiz_repo / "Makefile").read_text(encoding="utf-8")

    # Act
    objetivos = set(re.findall(r"^([a-z]+):", texto, flags=re.MULTILINE))
    recetas = [linea for linea in texto.splitlines() if linea.lstrip().startswith("uv run")]

    # Assert
    assert {"install", "lint", "format", "test", "check"} <= objetivos
    assert re.search(r"^check:.*\blint\b.*\btest\b", texto, flags=re.MULTILINE)
    assert "uv run ruff check ." in texto
    assert "uv run ruff format --check ." in texto
    assert "uv run pytest" in texto
    assert recetas and all(linea.startswith("\t") for linea in recetas), "recetas sin tabulador"


def test_sin_requirements_ni_notebooks(raiz_repo: Path) -> None:
    # Arrange
    archivos = _archivos_del_repo(raiz_repo)

    # Act
    prohibidos = [
        a.relative_to(raiz_repo)
        for a in archivos
        if a.suffix == ".ipynb" or (a.name.startswith("requirements") and a.suffix == ".txt")
    ]

    # Assert
    assert prohibidos == []


def test_ruff_no_excluye_scripts_ni_hooks(pyproject: dict[str, Any]) -> None:
    # Arrange
    ruff = pyproject["tool"]["ruff"]
    protegidas = ("scripts", ".claude")

    # Act
    excluidos = ruff.get("exclude", []) + ruff.get("extend-exclude", [])
    ignorados = list(ruff["lint"].get("per-file-ignores", {}))
    patrones = excluidos + ignorados

    # Assert
    assert not [p for p in patrones if p.lstrip("./").startswith(protegidas)]
