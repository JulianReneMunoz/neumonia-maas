# SPEC-004 · Configuración tipada con pydantic-settings

- **Estado:** Borrador <!-- Borrador → Aprobada → Implementada -->
- **Historia:** #? (confirmar con `uv run scripts/tablero.py issue SPEC-004`) · **Puntos:** 2 · **Milestone:** M3 · **Labels:** backend
- **Depende de:** SPEC-001
- **PR:** #N (se completa al abrirla)

## 1. Problema y contexto
El servicio necesita parámetros que cambian según el entorno: qué modelo de Hugging Face
cargar y en qué revisión, el umbral de decisión NORMAL/PNEUMONIA, el tamaño máximo de una
radiografía subida, el tiempo máximo de inferencia, los orígenes del frontend permitidos por
CORS y la URI de MLflow. Si esos valores quedan escritos a mano en cada módulo, cambiar el
umbral obliga a tocar código, aparecen valores duplicados o contradictorios entre capas y un
valor absurdo (umbral 1.5) solo se descubre cuando la API ya responde mal. Una configuración
única, tipada y validada al arrancar resuelve las tres cosas. Para la rúbrica importa porque
demuestra separación de configuración y código, ausencia de secretos en el repositorio y un
punto único del que leen las historias posteriores (SPEC-005 modelo/revisión, SPEC-007 umbral,
SPEC-013 tamaño máximo y timeout, SPEC-014 CORS, SPEC-027 MLflow).

## 2. Historia
**Como** operador del servicio, **quiero** configurar modelo, revisión, umbral, tamaño máximo
y CORS por variables de entorno **para** cambiar el comportamiento sin tocar código.

## 3. Requisitos
### Funcionales
- RF-1: Existe `src/neumonia/config.py` con una clase `Settings` (pydantic-settings) que lee
  variables de entorno con el prefijo `NEUMONIA_`.
- RF-2: `Settings` expone estos campos con sus valores por defecto documentados:

  | Campo | Variable | Tipo | Default | Lo consume |
  |---|---|---|---|---|
  | `model_id` | `NEUMONIA_MODEL_ID` | `str` | `lxyuan/vit-xray-pneumonia-classification` | SPEC-005 |
  | `model_revision` | `NEUMONIA_MODEL_REVISION` | `str` | `main` (provisional, ver pregunta 2) | SPEC-005 |
  | `threshold` | `NEUMONIA_THRESHOLD` | `float` en [0, 1] | `0.5` | SPEC-007, SPEC-012 |
  | `max_upload_mb` | `NEUMONIA_MAX_UPLOAD_MB` | `int` > 0 | `10` | SPEC-013 |
  | `timeout_s` | `NEUMONIA_TIMEOUT_S` | `float` > 0 | `30.0` | SPEC-013 |
  | `cors_origins` | `NEUMONIA_CORS_ORIGINS` | `list[str]` | `http://localhost:5173,http://127.0.0.1:5173` | SPEC-014 |
  | `mlflow_tracking_uri` | `NEUMONIA_MLFLOW_TRACKING_URI` | `str` | `http://127.0.0.1:5050` | SPEC-027 |

- RF-3: `NEUMONIA_THRESHOLD` fuera de [0, 1] (o no numérico) hace fallar la carga con un
  `pydantic.ValidationError` cuyo mensaje nombra la variable `NEUMONIA_THRESHOLD`, el rango
  permitido (0–1) y el valor recibido. Los extremos 0 y 1 son válidos.
- RF-4: `NEUMONIA_MAX_UPLOAD_MB` y `NEUMONIA_TIMEOUT_S` deben ser estrictamente positivos; si
  no, la carga falla con `ValidationError`.
- RF-5: `NEUMONIA_CORS_ORIGINS` acepta una lista separada por comas
  (`http://a:1,http://b:2`); se recortan espacios y se descartan elementos vacíos.
- RF-6: `Settings` ofrece dos propiedades derivadas de solo lectura: `model_ref`
  (`"<model_id>@<model_revision>"`, usado por /health, /model y MLflow) y `max_upload_bytes`
  (`max_upload_mb * 1024 * 1024`).
- RF-7: `get_settings() -> Settings` devuelve una instancia cacheada con
  `functools.lru_cache` (se construye una sola vez por proceso); `get_settings.cache_clear()`
  fuerza una relectura.
- RF-8: Orden de prioridad: variable de entorno > archivo `.env` del directorio de trabajo >
  default. Variables desconocidas se ignoran.
- RF-9: Existe `.env.example` en la raíz que documenta **todas** las variables de `Settings`
  (una línea `NEUMONIA_<CAMPO>=<default>` con un comentario que explica cada una) y no
  contiene secretos.
- RF-10: La dependencia `pydantic-settings` se añade con `uv add` (queda en `pyproject.toml`
  y `uv.lock`).

### No funcionales
- RNF-1: `neumonia.config` no importa FastAPI, Starlette, torch ni transformers; cualquier
  capa (`inference/`, `services/`, `api/`, `tracking/`, `scripts/`) puede usarlo.
- RNF-2: `Settings` es inmutable (`frozen=True`): nadie cambia la configuración en caliente.
- RNF-3: Sin secretos en `.env.example`, en los defaults ni en la representación (`repr`) de
  `Settings`; `.env` sigue ignorado por Git (ya lo está en `.gitignore`).
- RNF-4: Pruebas pytest con patrón AAA, sin red, con `monkeypatch`, aisladas del `.env` real
  del desarrollador y con la caché de `get_settings` limpia entre pruebas.
- RNF-5: Pasa `ruff` con las reglas de SPEC-001 (ANN, docstrings estilo Google) y pytest con
  `filterwarnings = error` (ninguna advertencia de pydantic).

## 4. Criterios de aceptación (Given-When-Then)
**AC-1** (backlog)
- **Dado** que no hay variables `NEUMONIA_*` en el entorno ni archivo `.env`
- **Cuando** cargo `Settings` (vía `get_settings()`)
- **Entonces** obtengo los valores por defecto documentados: umbral `0.5`, `max_upload_mb`
  `10`, modelo `lxyuan/vit-xray-pneumonia-classification` con su revisión por defecto, y el
  resto de la tabla de RF-2; `model_ref` es `lxyuan/vit-xray-pneumonia-classification@<rev>`
  y `max_upload_bytes` es `10 485 760`.

**AC-2** (backlog)
- **Dado** `NEUMONIA_THRESHOLD=1.5`
- **Cuando** cargo `Settings`
- **Entonces** falla la validación con un mensaje claro que menciona `NEUMONIA_THRESHOLD`, el
  rango 0–1 y el valor `1.5`. Lo mismo ocurre con `-0.1` y con un valor no numérico (`abc`).

**AC-3** (backlog)
- **Dado** el archivo `.env.example` de la raíz
- **Cuando** lo reviso
- **Entonces** documenta todas las variables de `Settings` (cada campo aparece como
  `NEUMONIA_<CAMPO>` y no sobra ninguna variable `NEUMONIA_*` inexistente), cargarlo produce
  exactamente los defaults y no contiene secretos (ni claves tipo `TOKEN`, `SECRET`,
  `PASSWORD`, `API_KEY` ni valores con forma de token de Hugging Face `hf_…`).

**AC-4** (sobrescritura)
- **Dado** `NEUMONIA_THRESHOLD=0.35`, `NEUMONIA_MAX_UPLOAD_MB=5` y
  `NEUMONIA_MODEL_REVISION=abc123`
- **Cuando** cargo `Settings`
- **Entonces** los campos toman esos valores (tipados: `0.35` float, `5` int) y `model_ref`
  termina en `@abc123`.

**AC-5** (bordes del umbral)
- **Dado** `NEUMONIA_THRESHOLD=0` o `NEUMONIA_THRESHOLD=1`
- **Cuando** cargo `Settings`
- **Entonces** la carga es válida y el umbral vale exactamente ese extremo.

**AC-6** (límites no positivos)
- **Dado** `NEUMONIA_MAX_UPLOAD_MB=0` o `NEUMONIA_TIMEOUT_S=-1`
- **Cuando** cargo `Settings`
- **Entonces** falla la validación con `ValidationError` que nombra el campo.

**AC-7** (CORS)
- **Dado** `NEUMONIA_CORS_ORIGINS=" http://localhost:5173 , http://localhost:8080 ,"`
- **Cuando** cargo `Settings`
- **Entonces** `cors_origins == ["http://localhost:5173", "http://localhost:8080"]`.

**AC-8** (caché)
- **Dado** que llamé `get_settings()` una vez
- **Cuando** lo llamo de nuevo
- **Entonces** recibo el mismo objeto (`is`); y si cambio una variable y llamo
  `get_settings.cache_clear()`, la siguiente llamada refleja el nuevo valor.

**AC-9** (prioridad `.env`)
- **Dado** un `.env` en el directorio de trabajo con `NEUMONIA_THRESHOLD=0.4`
- **Cuando** cargo `Settings` sin la variable de entorno, y luego con
  `NEUMONIA_THRESHOLD=0.3` exportada
- **Entonces** el umbral es `0.4` en el primer caso y `0.3` en el segundo.

**AC-10** (capas e inmutabilidad)
- **Dado** el módulo `neumonia.config`
- **Cuando** reviso sus imports y trato de asignar `settings.threshold = 0.9`
- **Entonces** no importa `fastapi`, `starlette`, `torch` ni `transformers`, y la asignación
  falla (`ValidationError` por instancia congelada).

## 5. Fuera de alcance
- Usar la configuración en otros módulos: cargar el modelo (SPEC-005), aplicar el umbral
  (SPEC-007), el límite de tamaño y el timeout (SPEC-013), el middleware CORS (SPEC-014) y
  el tracking (SPEC-027). Esas historias solo **leen** `get_settings()`.
- Fijar el commit SHA real del modelo (lo hace SPEC-005 con `huggingface_hub.model_info`).
- Parámetros de preprocesamiento (tamaño, CLAHE) y de experimentos: viven en
  `configs/*.yaml` (SPEC-006, SPEC-030), no en variables de entorno.
- Tags de MLflow como equipo o ambiente (SPEC-027 añadirá campos si los necesita; la prueba
  de `.env.example` le obligará a documentarlos).
- Gestión de secretos (no hay secretos en el proyecto) y configuración del frontend
  (`VITE_*`, SPEC-018 en adelante).

## 6. Métricas de éxito
- 10 AC verificados por 16 pruebas automáticas (19 casos) (piso del backlog: 5), todas en verde con
  `make check` y sin advertencias.
- 0 valores de configuración duplicados en código: las historias posteriores leen de
  `get_settings()` (se revisa en sus PR).
- Demo: `NEUMONIA_THRESHOLD=1.5 uv run python -c "from neumonia.config import get_settings; get_settings()"`
  muestra el error en español en menos de 1 s.

## 7. Preguntas abiertas
1. **Dependencia de SPEC-001 aún no fusionada.** `pyproject.toml`, `src/neumonia/`,
   `tests/conftest.py`, el Makefile, ruff (ANN, D estilo Google) y pytest con
   `filterwarnings = error` solo existen en la rama `feature/001-esqueleto-uv`; en `develop`
   todavía no. SPEC-004 se implementa después de fusionar SPEC-001, trayendo `develop` a
   esta rama con merge (sin rebase: la rama ya está en el remoto y `push --force` está
   prohibido). Si al implementar cambia algún nombre de SPEC-001, se ajusta con
   `docs(spec): ajuste …`.
2. **Revisión por defecto del modelo.** Mientras SPEC-005 no fije el SHA, el default es
   `main` (válido para Hugging Face, pero no reproducible). SPEC-005 lo sustituirá por el SHA
   en `config.py`, `.env.example` y `docs/backlog.yaml`. ¿Aceptas `main` como provisional, o
   prefieres un marcador inválido (p. ej. `PENDIENTE`) que obligue a fijarlo?
3. **Timeout por defecto.** Se propone `30.0` s para `NEUMONIA_TIMEOUT_S` (inferencia ViT en
   CPU más la primera llamada, más lenta). El backlog no da un valor; confirmar.
4. **Orígenes CORS por defecto.** Se proponen `http://localhost:5173` y
   `http://127.0.0.1:5173` (Vite). Si la demo con contenedores (SPEC de arranque) sirve el
   frontend en `8080`, ¿se añade ya o lo hace esa historia?
5. **Número de issue** de SPEC-004: confirmar con `uv run scripts/tablero.py issue SPEC-004`.
