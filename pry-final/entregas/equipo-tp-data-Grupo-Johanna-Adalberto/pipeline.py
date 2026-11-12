"""Lee CSV tipados y reemplaza las tablas de origen en una base DuckDB local."""

import argparse
import csv
from datetime import date
from decimal import Decimal
from pathlib import Path

import dlt

from generar_datos import RAIZ

COLUMNAS = {
    "productos": dict(
        id=int,
        nombre=str,
        categoria=str,
        costo_unitario=int,
        precio_venta=int,
        stock_inicial=int,
    ),
    "vendedores": dict(id=int, nombre=str, sucursal=str, fecha_alta=date.fromisoformat),
    "compras": dict(
        id=int,
        fecha=date.fromisoformat,
        producto_id=int,
        cantidad=int,
        costo_unitario=int,
        proveedor=str,
    ),
    "ventas": dict(
        id=int,
        fecha=date.fromisoformat,
        producto_id=int,
        cantidad=int,
        precio_unitario=int,
        descuento=Decimal,
        vendedor_id=int,
    ),
    "movimientos_stock": dict(
        id=int,
        fecha=date.fromisoformat,
        producto_id=int,
        tipo=str,
        cantidad=int,
        referencia_id=int,
    ),
}


def leer_csv(ruta, columnas):
    with ruta.open(encoding="utf-8", newline="") as archivo:
        lector = csv.DictReader(archivo)
        if lector.fieldnames != list(columnas):
            raise ValueError(f"Columnas inesperadas en {ruta.name}: {lector.fieldnames}")
        filas = [{campo: tipo(fila[campo]) for campo, tipo in columnas.items()} for fila in lector]
    if not filas:
        raise ValueError(f"No hay filas en {ruta.name}")
    if len(filas) != len({fila["id"] for fila in filas}):
        raise ValueError(f"IDs repetidos en {ruta.name}")
    return filas


def cargar_datos(carpeta=RAIZ / "data", base=RAIZ / "data.duckdb"):
    """Valida los cinco archivos antes de cargar una instantánea completa."""
    carpeta, base = Path(carpeta), Path(base).resolve()
    base.parent.mkdir(parents=True, exist_ok=True)
    recursos = [
        dlt.resource(
            leer_csv(carpeta / f"{tabla}.csv", columnas),
            name=tabla,
            primary_key="id",
            write_disposition="replace",
        )
        for tabla, columnas in COLUMNAS.items()
    ]
    dlt.config["runtime.dlthub_telemetry"] = False
    flujo = dlt.pipeline(
        pipeline_name="minimercado",
        pipelines_dir=str(base.parent / ".dlt" / base.stem),
        dataset_name="raw",
        destination=dlt.destinations.duckdb(str(base)),
    )
    info = flujo.run(recursos)
    info.raise_on_failed_jobs()
    return info


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--carpeta", type=Path, default=RAIZ / "data")
    parser.add_argument("--base", type=Path, default=RAIZ / "data.duckdb")
    args = parser.parse_args()
    print(cargar_datos(args.carpeta, args.base))
