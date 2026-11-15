"""Configuración tipada del servicio, leída de variables de entorno ``NEUMONIA_*`` y de ``.env``.

Es el único lugar donde se definen los parámetros que cambian según el entorno (modelo,
revisión, umbral, límites, CORS y MLflow). Las demás capas solo leen ``get_settings()``.
Este módulo no importa FastAPI, torch ni transformers: cualquier capa puede usarlo.

Prioridad de las fuentes: variable de entorno > archivo ``.env`` del directorio de trabajo >
valor por defecto.
"""

from functools import lru_cache
from typing import Annotated, Final

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict

DEFAULT_MODEL_ID: Final = "lxyuan/vit-xray-pneumonia-classification"
# Provisional: SPEC-005 fija aquí el commit SHA del modelo.
DEFAULT_MODEL_REVISION: Final = "main"


class Settings(BaseSettings):
    """Configuración del servicio leída de variables ``NEUMONIA_*`` y de ``.env``.

    Attributes:
        model_id: Repositorio del modelo en Hugging Face Hub.
        model_revision: Revisión (commit SHA) del modelo.
        threshold: Umbral de decisión: ``p(PNEUMONIA) >= threshold`` → PNEUMONIA. Rango 0–1.
        max_upload_mb: Tamaño máximo de la imagen subida, en MB (> 0).
        timeout_s: Tiempo máximo de inferencia, en segundos (> 0).
        cors_origins: Orígenes del frontend permitidos por CORS.
        mlflow_tracking_uri: URI del servidor de MLflow.
    """

    model_config = SettingsConfigDict(
        env_prefix="NEUMONIA_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        frozen=True,
        # Los campos model_* chocan con el espacio protegido de pydantic; sin esto habría
        # una advertencia y pytest (filterwarnings = error) fallaría.
        protected_namespaces=(),
    )

    model_id: str = DEFAULT_MODEL_ID
    model_revision: str = DEFAULT_MODEL_REVISION
    threshold: float = 0.5
    max_upload_mb: int = Field(default=10, gt=0)
    timeout_s: float = Field(default=30.0, gt=0)
    # NoDecode: la lista llega como texto separado por comas, no como JSON.
    cors_origins: Annotated[list[str], NoDecode] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]
    mlflow_tracking_uri: str = "http://127.0.0.1:5050"

    @field_validator("threshold")
    @classmethod
    def _validar_umbral(cls, valor: float) -> float:
        """Rechaza umbrales fuera de [0, 1] con un mensaje que nombra la variable.

        Args:
            valor: Umbral ya convertido a ``float`` por pydantic.

        Returns:
            El mismo valor si está en el rango.

        Raises:
            ValueError: Si el umbral es menor que 0 o mayor que 1.
        """
        if not 0.0 <= valor <= 1.0:
            raise ValueError(f"NEUMONIA_THRESHOLD debe estar en el rango 0–1 (recibido: {valor})")
        return valor

    @field_validator("cors_origins", mode="before")
    @classmethod
    def _separar_origenes(cls, valor: object) -> object:
        """Convierte ``"http://a:1, http://b:2,"`` en ``["http://a:1", "http://b:2"]``.

        Args:
            valor: Texto separado por comas (desde el entorno) o una lista ya armada.

        Returns:
            La lista de orígenes sin espacios ni elementos vacíos; otros tipos pasan tal cual.
        """
        if isinstance(valor, str):
            return [origen.strip() for origen in valor.split(",") if origen.strip()]
        return valor

    @property
    def model_ref(self) -> str:
        """Referencia ``org/modelo@revision`` que muestran /health, /model y MLflow."""
        return f"{self.model_id}@{self.model_revision}"

    @property
    def max_upload_bytes(self) -> int:
        """Tamaño máximo de la imagen subida, en bytes."""
        return self.max_upload_mb * 1024 * 1024


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Devuelve la configuración del proceso (se construye una sola vez).

    Returns:
        La instancia de ``Settings``, cacheada. ``get_settings.cache_clear()`` fuerza a
        leerla de nuevo.
    """
    return Settings()
