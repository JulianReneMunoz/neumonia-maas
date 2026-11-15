import ast
import fnmatch
import json
import os
import re
from pathlib import Path

import pytest
from pydantic import ValidationError

from neumonia.config import DEFAULT_MODEL_ID, DEFAULT_MODEL_REVISION, Settings, get_settings

PROHIBIDOS_EN_CONFIG = {"fastapi", "starlette", "torch", "transformers"}


@pytest.fixture
def entorno_limpio(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> pytest.MonkeyPatch:
    """Borra toda variable NEUMONIA_* y cambia el cwd a tmp_path (sin .env real)."""
    for nombre in list(os.environ):
        if nombre.upper().startswith("NEUMONIA_"):
            monkeypatch.delenv(nombre)
    monkeypatch.chdir(tmp_path)
    return monkeypatch


def test_defaults_sin_variables_de_entorno(entorno_limpio: pytest.MonkeyPatch) -> None:
    # Arrange: entorno sin NEUMONIA_* y sin .env

    # Act
    settings = get_settings()

    # Assert
    assert settings.model_id == "lxyuan/vit-xray-pneumonia-classification"
    assert settings.model_revision == DEFAULT_MODEL_REVISION
    assert settings.threshold == 0.5
    assert settings.max_upload_mb == 10
    assert settings.timeout_s == 30.0
    assert settings.cors_origins == ["http://localhost:5173", "http://127.0.0.1:5173"]
    assert settings.mlflow_tracking_uri == "http://127.0.0.1:5050"


def test_propiedades_derivadas_model_ref_y_bytes(entorno_limpio: pytest.MonkeyPatch) -> None:
    # Arrange
    settings = get_settings()

    # Act
    referencia = settings.model_ref
    limite_bytes = settings.max_upload_bytes

    # Assert
    assert referencia == f"{DEFAULT_MODEL_ID}@{DEFAULT_MODEL_REVISION}"
    assert limite_bytes == 10_485_760


def test_variables_de_entorno_sobrescriben_defaults(entorno_limpio: pytest.MonkeyPatch) -> None:
    # Arrange
    entorno_limpio.setenv("NEUMONIA_THRESHOLD", "0.35")
    entorno_limpio.setenv("NEUMONIA_MAX_UPLOAD_MB", "5")
    entorno_limpio.setenv("NEUMONIA_MODEL_REVISION", "abc123")

    # Act
    settings = get_settings()

    # Assert
    assert settings.threshold == 0.35
    assert isinstance(settings.threshold, float)
    assert settings.max_upload_mb == 5
    assert isinstance(settings.max_upload_mb, int)
    assert settings.model_ref.endswith("@abc123")


@pytest.mark.parametrize("valor", ["1.5", "-0.1"])
def test_umbral_fuera_de_rango_falla_con_mensaje_claro(
    entorno_limpio: pytest.MonkeyPatch, valor: str
) -> None:
    # Arrange
    entorno_limpio.setenv("NEUMONIA_THRESHOLD", valor)

    # Act
    with pytest.raises(ValidationError) as error:
        get_settings()

    # Assert
    mensaje = str(error.value)
    assert "NEUMONIA_THRESHOLD" in mensaje
    assert "0–1" in mensaje
    assert f"recibido: {valor}" in mensaje


def test_umbral_no_numerico_falla(entorno_limpio: pytest.MonkeyPatch) -> None:
    # Arrange
    entorno_limpio.setenv("NEUMONIA_THRESHOLD", "abc")

    # Act
    with pytest.raises(ValidationError) as error:
        get_settings()

    # Assert
    assert error.value.errors()[0]["loc"] == ("threshold",)


@pytest.mark.parametrize("valor", ["0", "1"])
def test_umbral_en_los_extremos_es_valido(entorno_limpio: pytest.MonkeyPatch, valor: str) -> None:
    # Arrange
    entorno_limpio.setenv("NEUMONIA_THRESHOLD", valor)

    # Act
    settings = get_settings()

    # Assert
    assert settings.threshold == float(valor)


@pytest.mark.parametrize(("variable", "valor"), [("MAX_UPLOAD_MB", "0"), ("TIMEOUT_S", "-1")])
def test_limites_no_positivos_fallan(
    entorno_limpio: pytest.MonkeyPatch, variable: str, valor: str
) -> None:
    # Arrange
    entorno_limpio.setenv(f"NEUMONIA_{variable}", valor)

    # Act
    with pytest.raises(ValidationError) as error:
        get_settings()

    # Assert
    assert error.value.errors()[0]["loc"] == (variable.lower(),)


def test_cors_origins_desde_lista_separada_por_comas(entorno_limpio: pytest.MonkeyPatch) -> None:
    # Arrange
    entorno_limpio.setenv(
        "NEUMONIA_CORS_ORIGINS", " http://localhost:5173 , http://localhost:8080 ,"
    )

    # Act
    settings = get_settings()

    # Assert
    assert settings.cors_origins == ["http://localhost:5173", "http://localhost:8080"]


def test_get_settings_devuelve_la_misma_instancia(entorno_limpio: pytest.MonkeyPatch) -> None:
    # Arrange
    primera = get_settings()

    # Act
    segunda = get_settings()

    # Assert
    assert segunda is primera


def test_get_settings_relee_tras_cache_clear(entorno_limpio: pytest.MonkeyPatch) -> None:
    # Arrange
    antes = get_settings()
    entorno_limpio.setenv("NEUMONIA_THRESHOLD", "0.7")

    # Act
    sin_limpiar = get_settings()
    get_settings.cache_clear()
    despues = get_settings()

    # Assert
    assert sin_limpiar is antes, "sin cache_clear se reutiliza la instancia"
    assert antes.threshold == 0.5
    assert despues.threshold == 0.7


def test_env_del_cwd_se_lee_y_el_entorno_tiene_prioridad(
    entorno_limpio: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    # Arrange
    (tmp_path / ".env").write_text("NEUMONIA_THRESHOLD=0.4\n", encoding="utf-8")

    # Act
    desde_archivo = get_settings().threshold
    entorno_limpio.setenv("NEUMONIA_THRESHOLD", "0.3")
    get_settings.cache_clear()
    desde_entorno = get_settings().threshold

    # Assert
    assert desde_archivo == 0.4
    assert desde_entorno == 0.3


def test_settings_es_inmutable(entorno_limpio: pytest.MonkeyPatch) -> None:
    # Arrange
    settings = get_settings()

    # Act / Assert
    with pytest.raises(ValidationError):
        settings.threshold = 0.9  # type: ignore[misc]
    assert isinstance(settings, Settings)


def test_config_no_importa_fastapi_ni_torch(raiz_repo: Path) -> None:
    # Arrange
    codigo = (raiz_repo / "src" / "neumonia" / "config.py").read_text(encoding="utf-8")

    # Act
    arbol = ast.parse(codigo)
    raices: set[str] = set()
    for nodo in ast.walk(arbol):
        if isinstance(nodo, ast.Import):
            raices.update(alias.name.split(".")[0] for alias in nodo.names)
        elif isinstance(nodo, ast.ImportFrom) and nodo.module:
            raices.add(nodo.module.split(".")[0])

    # Assert
    assert raices.isdisjoint(PROHIBIDOS_EN_CONFIG), raices & PROHIBIDOS_EN_CONFIG


def _variables_de_env_example(raiz: Path) -> dict[str, str]:
    """Pares ``NEUMONIA_X=valor`` de ``.env.example`` (se ignoran comentarios y vacíos)."""
    texto = (raiz / ".env.example").read_text(encoding="utf-8")
    pares = (linea.split("=", 1) for linea in texto.splitlines() if "=" in linea)
    return {clave.strip(): valor.strip() for clave, valor in pares if not clave.startswith("#")}


def test_env_example_documenta_todos_los_campos(raiz_repo: Path) -> None:
    # Arrange
    esperadas = {f"NEUMONIA_{campo.upper()}" for campo in Settings.model_fields}

    # Act
    documentadas = set(_variables_de_env_example(raiz_repo))

    # Assert
    assert esperadas - documentadas == set(), "campos sin documentar en .env.example"
    assert documentadas - esperadas == set(), "variables en .env.example que Settings no tiene"


def test_env_example_carga_exactamente_los_defaults(
    entorno_limpio: pytest.MonkeyPatch, raiz_repo: Path
) -> None:
    # Arrange
    archivo = raiz_repo / ".env.example"
    # pydantic-settings ignora en silencio un env_file inexistente: sin esto la prueba
    # pasaría aunque .env.example no existiera.
    assert archivo.is_file(), ".env.example no existe"

    # Act
    desde_ejemplo = Settings(_env_file=archivo)
    por_defecto = Settings(_env_file=None)

    # Assert
    assert desde_ejemplo == por_defecto


def test_env_example_no_contiene_secretos(raiz_repo: Path) -> None:
    # Arrange
    texto = (raiz_repo / ".env.example").read_text(encoding="utf-8")
    claves = _variables_de_env_example(raiz_repo)

    # Act
    claves_sensibles = [
        clave
        for clave in claves
        if any(palabra in clave for palabra in ("TOKEN", "SECRET", "PASSWORD", "API_KEY"))
    ]
    tokens_hf = re.findall(r"\bhf_[A-Za-z0-9]{10,}", texto)

    # Assert
    assert claves_sensibles == []
    assert tokens_hf == []


def test_claude_no_lee_env_con_secretos_pero_si_env_example(raiz_repo: Path) -> None:
    # Arrange
    ajustes = json.loads((raiz_repo / ".claude" / "settings.json").read_text(encoding="utf-8"))
    patrones = [
        regla.removeprefix("Read(./").removesuffix(")")
        for regla in ajustes["permissions"]["deny"]
        if regla.startswith("Read(./")
    ]

    # Act
    def bloqueado(nombre: str) -> bool:
        return any(fnmatch.fnmatchcase(nombre, patron) for patron in patrones)

    # Assert
    # Los archivos con secretos siguen protegidos...
    assert all(bloqueado(n) for n in (".env", ".env.local", ".env.development.local"))
    # ...pero .env.example no tiene secretos y debe poder escribirse y versionarse.
    assert not bloqueado(".env.example")
