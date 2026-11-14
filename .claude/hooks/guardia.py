"""Guardia de reglas del curso para Claude Code (hook PreToolUse).

Lee el evento del hook por stdin (JSON) y bloquea, con código de salida 2, las acciones
que la rúbrica del M3 penaliza: pip/requirements.txt, notebooks, Streamlit/Gradio/Dash,
commits o merges directos en main/develop, --no-verify y push --force.

Solo usa la biblioteca estándar para que funcione en Windows (Git Bash) y Linux.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

RAMAS_PROTEGIDAS = {"main", "develop"}
UI_PROHIBIDAS = re.compile(r"\b(streamlit|gradio|dash)\b", re.IGNORECASE)


def rama_actual(cwd: str | None) -> str:
    """Devuelve la rama actual de Git o una cadena vacía si no hay repositorio."""
    try:
        salida = subprocess.run(
            ["git", "branch", "--show-current"],
            capture_output=True,
            text=True,
            cwd=cwd or None,
            timeout=5,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return ""
    return salida.stdout.strip()


def revisar_comando(comando: str, cwd: str | None) -> str | None:
    """Devuelve el motivo del bloqueo para un comando de Bash, o None si está permitido."""
    texto = " ".join(comando.split())
    if re.search(r"(^|[\s;&|(])(pip3?|python3?\s+-m\s+pip|uv\s+pip)\s+install\b", texto):
        return "Prohibido pip: usa `uv add <paquete>` (o `uv add --dev`)."
    if re.search(r"\bpip3?\s+freeze\b", texto) or "requirements.txt" in texto:
        return "Prohibido requirements.txt: las dependencias viven en pyproject.toml + uv.lock."
    if re.search(r"\b(uv\s+add|pnpm\s+add|npm\s+install)\b", texto) and UI_PROHIBIDAS.search(texto):
        return "Streamlit, Gradio y Dash no se aceptan en el M3: la UI es el frontend React."
    if "--no-verify" in texto:
        return "No se permite saltar los hooks (--no-verify)."
    if re.search(r"\bgit\s+push\b.*(\s--force\b|\s-f\b|\s--force-with-lease\b)", texto):
        return "No se permite push --force."
    if re.search(r"\bgit\s+push\b.*\s(origin\s+)?(main|develop)(\s|$)", texto) and not re.search(
        r"\bgit\s+push\b.*\s(-d|--delete)\b", texto
    ):
        return "No se hace push directo a main/develop: todo entra por PR (`/pr`)."
    if re.search(r"\bgit\s+(commit|merge|rebase|cherry-pick)\b", texto):
        rama = rama_actual(cwd)
        if rama in RAMAS_PROTEGIDAS:
            return (
                f"Estás en `{rama}`: no se hacen commits ni merges directos. "
                "Crea la rama de la historia con `/spec SPEC-NNN`."
            )
    return None


def revisar_archivo(ruta: str) -> str | None:
    """Devuelve el motivo del bloqueo para escribir un archivo, o None si está permitido."""
    nombre = Path(ruta).name.lower()
    if nombre.endswith(".ipynb"):
        return "Prohibidos los notebooks: usa módulos .py en src/ o scripts/."
    if nombre == "requirements.txt":
        return "Prohibido requirements.txt: usa `uv add`."
    if nombre.endswith((".pt", ".pth", ".h5", ".onnx", ".joblib", ".safetensors", ".ckpt")):
        return "Los pesos del modelo no se versionan: se descargan con scripts/descargar_modelo.py."
    return None


def main() -> int:
    """Punto de entrada del hook: 0 permite la acción, 2 la bloquea con un mensaje."""
    try:
        evento = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0
    herramienta = evento.get("tool_name", "")
    entrada = evento.get("tool_input", {}) or {}
    cwd = evento.get("cwd")
    motivo: str | None = None
    if herramienta == "Bash":
        motivo = revisar_comando(str(entrada.get("command", "")), cwd)
    elif herramienta in {"Write", "Edit", "MultiEdit", "NotebookEdit"}:
        ruta = entrada.get("file_path") or entrada.get("notebook_path") or ""
        motivo = revisar_archivo(str(ruta))
    if motivo:
        print(f"[guardia] Bloqueado: {motivo}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
