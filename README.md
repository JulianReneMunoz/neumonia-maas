# neumonia-maas

Servicio de apoyo a la lectura de radiografías de tórax. Un cliente web desacoplado
(React) envía la imagen a una API FastAPI que clasifica **NORMAL / PNEUMONIA** con un modelo
preentrenado de Hugging Face Hub (`lxyuan/vit-xray-pneumonia-classification`, Apache-2.0).

> Proyecto del curso *Gestión de Proyectos en IA y Ciencia de Datos* (UAO, 2026-2S) — Módulo 3.
> Herramienta de apoyo; **no reemplaza el criterio clínico**.

🚧 README inicial. La historia **SPEC-037** lo completa (badges, arquitectura, instalación,
uso y estructura).

## Instalación y calidad
Requisitos: [uv](https://docs.astral.sh/uv/) (instala Python 3.13 solo si no lo tienes).
Este proyecto **solo usa uv**: nada de `pip` ni `requirements.txt`.

```bash
uv sync        # instala las dependencias exactas de uv.lock en .venv
make check     # compuerta de calidad: ruff (estilo, imports, anotaciones, docstrings) + pytest
```

Sin `make` (por ejemplo en PowerShell), los equivalentes directos son:

| `make` | Equivalente con uv |
|---|---|
| `make install` | `uv sync` |
| `make lint` | `uv run ruff check .` y `uv run ruff format --check .` |
| `make format` | `uv run ruff format .` y `uv run ruff check --fix .` |
| `make test` | `uv run pytest` |
| `make check` | `make lint` + `make test` |

Versión instalada: `uv run python -c "import neumonia; print(neumonia.__version__)"`.

## Enlaces
- Tablero Kanban: _(URL del Project, se agrega tras `bootstrap_github.py`)_
- Backlog y specs SDD: [`docs/backlog.yaml`](docs/backlog.yaml) · [`specs/`](specs/)
- Plan: [`docs/plan-semana.md`](docs/plan-semana.md) · Guion: [`docs/guion-sustentacion.md`](docs/guion-sustentacion.md) · Ficha: [`docs/ficha-entrega.md`](docs/ficha-entrega.md)
- Cómo trabaja el equipo con Claude Code: [`CLAUDE.md`](CLAUDE.md)

## Licencia
MIT — ver [LICENSE](LICENSE). El modelo base conserva su licencia Apache-2.0.
