"""Verifica que el entorno del curso esté listo.

Uso:
    python u1-entorno/tarea/verificar_entorno.py

Termina con código 0 e imprime OK si todo está bien; con código 1 si falta algo.
"""

from __future__ import annotations

import importlib.metadata as metadata
import os
import shutil
import subprocess
import sys

PYTHON_MINIMO = (3, 11)
PAQUETES = ["pytest", "ruff", "pre-commit"]
HERRAMIENTAS = ["git"]


def version_python_ok(version: tuple[int, ...] = tuple(sys.version_info)) -> bool:
    """Indica si la versión de Python alcanza el mínimo del curso."""
    return tuple(version[:2]) >= PYTHON_MINIMO


def version_paquete(nombre: str) -> str | None:
    """Devuelve la versión instalada de un paquete, o None si no está."""
    try:
        return metadata.version(nombre)
    except metadata.PackageNotFoundError:
        return None


def version_herramienta(nombre: str) -> str | None:
    """Devuelve la salida de `<herramienta> --version`, o None si no existe."""
    if shutil.which(nombre) is None:
        return None
    salida = subprocess.run(
        [nombre, "--version"], capture_output=True, text=True, check=False
    )
    return (salida.stdout or salida.stderr).strip()


def tipo_de_entorno() -> str:
    """Describe dónde se está ejecutando (informativo, no hace fallar la prueba)."""
    if os.environ.get("CODESPACES") == "true":
        return "GitHub Codespaces"
    if os.path.exists("/.dockerenv") or os.environ.get("REMOTE_CONTAINERS"):
        return "Dev Container local"
    return "fuera de un contenedor"


def main() -> int:
    problemas: list[str] = []
    print(f"Entorno: {tipo_de_entorno()}")

    version = ".".join(str(n) for n in sys.version_info[:3])
    print(f"Python: {version}")
    if not version_python_ok():
        minimo = ".".join(str(n) for n in PYTHON_MINIMO)
        problemas.append(f"Python {minimo} o superior (hay {version})")

    for nombre in PAQUETES:
        encontrada = version_paquete(nombre)
        print(f"{nombre}: {encontrada or 'NO ENCONTRADO'}")
        if encontrada is None:
            problemas.append(f"instalar {nombre} (pip install -r requirements.txt)")

    for nombre in HERRAMIENTAS:
        encontrada = version_herramienta(nombre)
        print(f"{nombre}: {encontrada or 'NO ENCONTRADO'}")
        if encontrada is None:
            problemas.append(f"instalar {nombre}")

    if problemas:
        print("\nFALTA:")
        for problema in problemas:
            print(f"  - {problema}")
        return 1

    print("\nOK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
