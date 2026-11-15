import re
from typing import Any

import neumonia

SEMVER = re.compile(r"^\d+\.\d+\.\d+$")


def test_version_tiene_formato_semver() -> None:
    # Arrange
    version = neumonia.__version__

    # Act
    coincide = SEMVER.match(version)

    # Assert
    assert coincide is not None, f"versión no es X.Y.Z: {version!r}"


def test_version_coincide_con_pyproject(pyproject: dict[str, Any]) -> None:
    # Arrange
    esperada = pyproject["project"]["version"]

    # Act
    obtenida = neumonia.__version__

    # Assert
    assert obtenida == esperada
