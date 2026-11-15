# Plan · SPEC-004

## 1. Diseño técnico
| Archivo | Cambio |
|---|---|
| `pyproject.toml` / `uv.lock` | **Modificar** con `uv add "pydantic-settings>=2.7"` (trae `pydantic` 2.x). Nunca a mano ni con pip. |
| `src/neumonia/config.py` | **Crear.** Clase `Settings(BaseSettings)`, validadores, propiedades `model_ref` y `max_upload_bytes`, función `get_settings()` con `lru_cache`, y constantes de default. |
| `.env.example` | **Crear** en la raíz. Una variable por campo con su default y un comentario en español. Ya está permitido por `.gitignore` (`!.env.example`). |
| `tests/conftest.py` | **Modificar** (creado en SPEC-001): fixture `autouse` `_cache_settings_limpia` que llama `get_settings.cache_clear()` antes y después de cada prueba, para que ninguna prueba (de esta ni de futuras historias) herede configuración de otra. |
| `tests/unit/test_config.py` | **Crear.** Fixture local `entorno_limpio` y las pruebas de §5. |
| `README.md` | **Modificar** mínimamente: sección «Configuración» que remite a `.env.example` y explica la prioridad entorno > `.env` > default. |

### Firmas públicas
```python
# src/neumonia/config.py
DEFAULT_MODEL_ID: Final = "lxyuan/vit-xray-pneumonia-classification"
DEFAULT_MODEL_REVISION: Final = "main"  # provisional: SPEC-005 fija el SHA

class Settings(BaseSettings):
    """Configuración del servicio leída de variables NEUMONIA_* y de .env."""

    model_config = SettingsConfigDict(
        env_prefix="NEUMONIA_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        frozen=True,
        protected_namespaces=(),   # evita el aviso por campos model_* con filterwarnings=error
    )

    model_id: str = DEFAULT_MODEL_ID
    model_revision: str = DEFAULT_MODEL_REVISION
    threshold: float = 0.5
    max_upload_mb: int = Field(default=10, gt=0)
    timeout_s: float = Field(default=30.0, gt=0)
    cors_origins: Annotated[list[str], NoDecode] = [
        "http://localhost:5173", "http://127.0.0.1:5173",
    ]
    mlflow_tracking_uri: str = "http://127.0.0.1:5050"

    @field_validator("threshold")
    @classmethod
    def _validar_umbral(cls, valor: float) -> float: ...

    @field_validator("cors_origins", mode="before")
    @classmethod
    def _separar_origenes(cls, valor: object) -> object: ...

    @property
    def model_ref(self) -> str: ...          # "org/modelo@rev"

    @property
    def max_upload_bytes(self) -> int: ...   # max_upload_mb * 1024 * 1024


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Devuelve la configuración del proceso (se construye una sola vez)."""
```

```python
# tests/conftest.py (añadido)
@pytest.fixture(autouse=True)
def _cache_settings_limpia() -> Iterator[None]: ...

# tests/unit/test_config.py
@pytest.fixture
def entorno_limpio(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> pytest.MonkeyPatch:
    """Borra toda variable NEUMONIA_* y cambia el cwd a tmp_path (sin .env real)."""
```

## 2. Contratos
**Variables de entorno** (prefijo `NEUMONIA_`, nombres sin distinguir mayúsculas):

| Variable | Tipo / regla | Default | Error si… |
|---|---|---|---|
| `NEUMONIA_MODEL_ID` | `str` | `lxyuan/vit-xray-pneumonia-classification` | — |
| `NEUMONIA_MODEL_REVISION` | `str` | `main` (provisional) | — |
| `NEUMONIA_THRESHOLD` | `float`, 0 ≤ x ≤ 1 | `0.5` | fuera de rango o no numérico |
| `NEUMONIA_MAX_UPLOAD_MB` | `int` > 0 | `10` | ≤ 0 o no entero |
| `NEUMONIA_TIMEOUT_S` | `float` > 0 | `30.0` | ≤ 0 |
| `NEUMONIA_CORS_ORIGINS` | lista separada por comas | `http://localhost:5173,http://127.0.0.1:5173` | — (vacíos se descartan) |
| `NEUMONIA_MLFLOW_TRACKING_URI` | `str` | `http://127.0.0.1:5050` | — |

**Mensaje de error del umbral** (texto del `ValueError` que pydantic envuelve en
`ValidationError`):
```
NEUMONIA_THRESHOLD debe estar en el rango 0–1 (recibido: 1.5)
```
Un valor no numérico (`abc`) lo rechaza antes el tipo `float` de pydantic
(`Input should be a valid number`), con el campo `threshold` en la ubicación del error.

**Formato de `.env.example`:**
```dotenv
# Configuración de neumonia-maas. Copia este archivo a .env y ajusta.
# Sin secretos: este proyecto no usa tokens ni contraseñas.

# Modelo de Hugging Face Hub y revisión (commit SHA; la fija SPEC-005).
NEUMONIA_MODEL_ID=lxyuan/vit-xray-pneumonia-classification
NEUMONIA_MODEL_REVISION=main
# Umbral de decisión: p(PNEUMONIA) >= umbral → PNEUMONIA. Rango 0–1.
NEUMONIA_THRESHOLD=0.5
# ... (una entrada comentada por campo, mismos defaults que config.py)
```

**Prioridad de fuentes:** argumentos explícitos a `Settings(...)` > variables de entorno >
`.env` del cwd > defaults del código.

## 3. Decisiones de diseño
| Decisión | Alternativas descartadas | Por qué |
|---|---|---|
| `pydantic-settings` con `BaseSettings` y prefijo `NEUMONIA_` | `os.environ.get` disperso; `python-dotenv` + dataclass; `dynaconf` | Lo pide el backlog; valida y convierte tipos en un solo sitio, y FastAPI ya trae pydantic (sin otra familia de dependencias). El prefijo evita choques con variables del sistema. |
| Validador propio del umbral con mensaje en español que nombra `NEUMONIA_THRESHOLD` | `Field(ge=0, le=1)` | El mensaje genérico de pydantic («less than or equal to 1») no dice qué variable cambiar; AC-2 exige un mensaje claro para el operador. Para tamaño y timeout basta `Field(gt=0)`. |
| `get_settings()` con `lru_cache(maxsize=1)` | Instancia global `settings = Settings()` al importar | Con la global, un `.env` malo rompe cualquier `import` (incluidas las pruebas) y no se puede recargar; con la función, la carga es perezosa, se cachea y `cache_clear()` permite probar y que FastAPI la inyecte con `Depends(get_settings)` más adelante. |
| `frozen=True` | Settings mutables | La configuración se decide al arrancar; inmutable evita cambios en caliente entre peticiones y hace la instancia segura de compartir. |
| `cors_origins` como lista separada por comas (`NoDecode` + validador `before`) | JSON (`["http://…"]`, el formato por defecto de pydantic-settings para listas) | Las comillas y corchetes de JSON son incómodos en PowerShell y en `.env`; la coma es lo habitual. Requiere `pydantic-settings>=2.7`. |
| Default de revisión `main` provisional | Marcador `PENDIENTE`; dejarlo obligatorio | `main` deja que el sistema funcione antes de SPEC-005; un campo obligatorio rompería AC-1. Queda como pregunta abierta y SPEC-005 lo sustituye por el SHA. |
| `extra="ignore"` | `extra="forbid"` | Un `.env` puede traer variables de otras herramientas (p. ej. `VITE_*`); con `forbid` el backend no arrancaría. |
| Pruebas aisladas: `monkeypatch.delenv` de toda `NEUMONIA_*` + `monkeypatch.chdir(tmp_path)` | Pasar `_env_file=None` en cada prueba | AC-1 se prueba por el camino real (`get_settings()`), sin parámetros especiales; cambiar el cwd garantiza que el `.env` del desarrollador no contamine el resultado. |
| Prueba que compara `Settings.model_fields` con las claves de `.env.example` en ambos sentidos, y que cargar `.env.example` da los defaults | Revisión manual del archivo | Si una historia futura añade un campo sin documentarlo (o cambia un default en un solo lado), la prueba falla: AC-3 deja de depender de la memoria. |
| Limpieza de la caché en `tests/conftest.py` (`autouse`) | Limpiar solo en `test_config.py` | Las pruebas de API de historias futuras también usarán `get_settings()`; una limpieza global evita fugas entre módulos de prueba. |

## 4. Riesgos
- **SPEC-001 no fusionada:** sin `pyproject.toml` no hay dónde hacer `uv add`. Mitigación:
  implementar tras fusionar SPEC-001 y traer `develop` con merge, nunca rebase
  (pregunta abierta 1).
- **Advertencias de pydantic con `filterwarnings = error`:** campos `model_*` pueden avisar
  por el espacio protegido `model_`. Mitigación: `protected_namespaces=()` en la config; si
  aparece otra advertencia, se corrige la causa, nunca se quita `error`.
- **`.env` real del desarrollador** cambia los defaults y hace fallar AC-1 de forma
  intermitente. Mitigación: fixture `entorno_limpio` con `chdir(tmp_path)` y `delenv`.
- **Caché obsoleta entre pruebas:** una prueba fija una variable y otra recibe el objeto
  viejo. Mitigación: fixture `autouse` con `cache_clear()` antes y después.
- **Windows:** `NEUMONIA_THRESHOLD=1.5 uv run …` no funciona en PowerShell. Mitigación: la
  demo documenta ambas formas (`$env:NEUMONIA_THRESHOLD="1.5"; uv run …`).
- **Versión de pydantic-settings sin `NoDecode`** (< 2.7). Mitigación: `uv add
  "pydantic-settings>=2.7"`.

## 5. Estrategia de pruebas
| Prueba (archivo::nombre) | Cubre |
|---|---|
| `tests/unit/test_config.py::test_defaults_sin_variables_de_entorno` | AC-1, RF-1, RF-2 |
| `tests/unit/test_config.py::test_propiedades_derivadas_model_ref_y_bytes` | AC-1, RF-6 |
| `tests/unit/test_config.py::test_variables_de_entorno_sobrescriben_defaults` | AC-4, RF-8 |
| `tests/unit/test_config.py::test_umbral_fuera_de_rango_falla_con_mensaje_claro[1.5]` / `[-0.1]` | AC-2, RF-3 |
| `tests/unit/test_config.py::test_umbral_no_numerico_falla` | AC-2, RF-3 |
| `tests/unit/test_config.py::test_umbral_en_los_extremos_es_valido[0]` / `[1]` | AC-5, RF-3 |
| `tests/unit/test_config.py::test_limites_no_positivos_fallan[MAX_UPLOAD_MB-0]` / `[TIMEOUT_S--1]` | AC-6, RF-4 |
| `tests/unit/test_config.py::test_cors_origins_desde_lista_separada_por_comas` | AC-7, RF-5 |
| `tests/unit/test_config.py::test_get_settings_devuelve_la_misma_instancia` | AC-8, RF-7 |
| `tests/unit/test_config.py::test_get_settings_relee_tras_cache_clear` | AC-8, RF-7 |
| `tests/unit/test_config.py::test_env_del_cwd_se_lee_y_el_entorno_tiene_prioridad` | AC-9, RF-8 |
| `tests/unit/test_config.py::test_settings_es_inmutable` | AC-10, RNF-2 |
| `tests/unit/test_config.py::test_config_no_importa_fastapi_ni_torch` (analiza los imports del archivo con `ast`) | AC-10, RNF-1 |
| `tests/unit/test_config.py::test_env_example_documenta_todos_los_campos` (ambos sentidos) | AC-3, RF-9 |
| `tests/unit/test_config.py::test_env_example_carga_exactamente_los_defaults` (`Settings(_env_file=raiz/.env.example)` == `Settings(_env_file=None)`) | AC-3, RF-9 |
| `tests/unit/test_config.py::test_env_example_no_contiene_secretos` | AC-3, RNF-3 |

Todas con patrón AAA (comentarios `# Arrange / # Act / # Assert`), sin red, sin GPU, usando
`monkeypatch`, `tmp_path` y la fixture `raiz_repo` de SPEC-001. Verificación manual
complementaria (demo): ver T9 de `tasks.md`.

Total planeado: 16 funciones de prueba, 19 casos con la parametrización (piso del backlog: 5).

## 6. Cómo explicarlo en la sustentación
- Toda la configuración vive en una sola clase, `Settings`: cada parámetro tiene tipo, valor
  por defecto y regla. Se cambia con variables `NEUMONIA_*` o un archivo `.env`, sin tocar
  código; `.env.example` es el «manual» de esas variables y una prueba garantiza que está
  completo y sin secretos.
- Si alguien pone un umbral imposible (1.5), el servicio no arranca y dice exactamente qué
  variable corregir y cuál es el rango; es mejor fallar al inicio que dar diagnósticos
  incorrectos.
- `get_settings()` lee la configuración una vez y la reutiliza (caché), igual que el modelo
  se carga una sola vez; en las pruebas se limpia la caché y se aísla el entorno para que
  cada prueba vea solo lo que ella misma configura.
