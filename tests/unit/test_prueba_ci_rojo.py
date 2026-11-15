# PRUEBA DESCARTABLE (SPEC-002, T10): demuestra que un test roto deja el check `ci` en rojo
# y que la protección de ramas bloquea la fusión. Esta PR se cierra sin fusionar.


def test_falla_a_proposito() -> None:
    # Arrange
    esperado = 1

    # Act
    obtenido = 2

    # Assert
    assert obtenido == esperado, "test roto a propósito para AC-2 de SPEC-002"
