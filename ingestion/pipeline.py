from dagster import asset, sensor, SensorEvaluationContext, RunRequest
import dlt
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

CSV_PATH = ROOT / "data"
DB_PATH = ROOT / "minimarket.duckdb"


@dlt.resource(name="raw_productos", write_disposition="replace")
def cargar_productos():
    df = pd.read_csv(CSV_PATH / "productos.csv")
    yield df.to_dict(orient="records")


@dlt.resource(name="raw_vendedores", write_disposition="replace")
def cargar_vendedores():
    df = pd.read_csv(CSV_PATH/"vendedores.csv")
    yield df.to_dict(orient="records")


@dlt.resource(name="raw_compras", write_disposition="replace")
def cargar_compras():
    df = pd.read_csv(CSV_PATH/"compras.csv")
    yield df.to_dict(orient="records")


@dlt.resource(name="raw_ventas", write_disposition="replace")
def cargar_ventas():
    df = pd.read_csv(CSV_PATH/"ventas.csv")
    yield df.to_dict(orient="records")


@dlt.resource(name="raw_movimientos_stock", write_disposition="replace")
def cargar_movimientos_stock():
    df = pd.read_csv(CSV_PATH/"movimientos_stock.csv")
    yield df.to_dict(orient="records")


@asset(deps=["generar_datos_asset"], group_name="ingesta")
def ejecutar_ingesta():
    pipeline = dlt.pipeline(
        pipeline_name="minimarket_ingestion",
        destination=dlt.destinations.duckdb(str(DB_PATH)),
        dataset_name="raw_data"
    )
    info = pipeline.run([
        cargar_productos(),
        cargar_vendedores(),
        cargar_compras(),
        cargar_ventas(),
        cargar_movimientos_stock()
    ])
    print("=== Ingesta con dlt completa ===")
    print(info)

if __name__ == "__main__":
    ejecutar_ingesta()
