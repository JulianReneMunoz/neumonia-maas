"""Neumonía MaaS: apoyo a la lectura de radiografías de tórax (NORMAL / PNEUMONIA).

El paquete se organiza en tres capas: ``inference`` (modelo), ``services`` (orquestación)
y ``api`` (FastAPI). La versión se lee de los metadatos instalados, cuya única fuente
de verdad es ``project.version`` en ``pyproject.toml``.
"""

from importlib.metadata import version

__version__: str = version("neumonia")
