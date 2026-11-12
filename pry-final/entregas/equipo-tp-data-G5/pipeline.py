"""Ingesta con dlt: carga los CSV de data/ en data.duckdb, esquema raw.

Es idempotente: cada tabla usa merge por su clave primaria "id", así que
volver a ejecutar el script actualiza los registros en lugar de duplicarlos.
Uso: python pipeline.py
"""

import csv
from pathlib import Path

import dlt

CARPETA = Path(__file__).resolve().parent
CARPETA_DATOS = CARPETA / "data"
RUTA_BD = CARPETA / "data.duckdb"
TABLAS = ["productos", "vendedores", "compras", "ventas", "movimientos_stock"]


def leer_csv(ruta: Path) -> list[dict]:
    """Lee un CSV y devuelve sus filas como diccionarios (todos los valores en texto)."""
    with ruta.open(encoding="utf-8", newline="") as archivo:
        return list(csv.DictReader(archivo))


def recurso_csv(tabla: str, carpeta: Path):
    """Crea un recurso dlt para un archivo CSV, con merge por id (idempotente)."""

    @dlt.resource(name=tabla, primary_key="id", write_disposition="merge")
    def _filas():
        yield leer_csv(carpeta / f"{tabla}.csv")

    return _filas


@dlt.source(name="minimercado")
def minimercado(carpeta: Path = CARPETA_DATOS):
    """Fuente dlt con un recurso por cada archivo de data/."""
    return [recurso_csv(tabla, carpeta) for tabla in TABLAS]


def construir_pipeline(ruta_bd: Path = RUTA_BD) -> dlt.Pipeline:
    """Pipeline hacia data.duckdb; las tablas quedan en el esquema raw."""
    return dlt.pipeline(
        pipeline_name="minimercado",
        destination=dlt.destinations.duckdb(credentials=str(ruta_bd)),
        dataset_name="raw",
    )


def cargar(ruta_bd: Path = RUTA_BD, carpeta: Path = CARPETA_DATOS):
    """Ejecuta la ingesta completa y devuelve la información de carga de dlt."""
    return construir_pipeline(ruta_bd).run(minimercado(carpeta))


def main() -> None:
    print(cargar())


if __name__ == "__main__":
    main()
