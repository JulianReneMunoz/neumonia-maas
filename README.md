# neumonia-maas

Servicio de apoyo a la lectura de radiografías de tórax. Un cliente web desacoplado
(React) envía la imagen a una API FastAPI que clasifica **NORMAL / PNEUMONIA** con un modelo
preentrenado de Hugging Face Hub (`lxyuan/vit-xray-pneumonia-classification`, Apache-2.0).

> Proyecto del curso *Gestión de Proyectos en IA y Ciencia de Datos* (UAO, 2026-2S) — Módulo 3.
> Herramienta de apoyo; **no reemplaza el criterio clínico**.

🚧 README inicial. La historia **SPEC-037** lo completa (badges, arquitectura, instalación,
uso y estructura).

## Enlaces
- Tablero Kanban: _(URL del Project, se agrega tras `bootstrap_github.py`)_
- Backlog y specs SDD: [`docs/backlog.yaml`](docs/backlog.yaml) · [`specs/`](specs/)
- Plan: [`docs/plan-semana.md`](docs/plan-semana.md) · Guion: [`docs/guion-sustentacion.md`](docs/guion-sustentacion.md) · Ficha: [`docs/ficha-entrega.md`](docs/ficha-entrega.md)
- Cómo trabaja el equipo con Claude Code: [`CLAUDE.md`](CLAUDE.md)

## Licencia
MIT — ver [LICENSE](LICENSE). El modelo base conserva su licencia Apache-2.0.
