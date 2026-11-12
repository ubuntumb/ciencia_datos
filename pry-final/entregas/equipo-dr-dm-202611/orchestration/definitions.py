import os
import subprocess
import sys

from dagster import Definitions, asset

# Obtener la ruta absoluta de la raíz del proyecto
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def _ensambrar_path():
    """Garantiza que la raíz del proyecto esté en sys.path dentro del worker."""
    if ROOT_DIR not in sys.path:
        sys.path.insert(0, ROOT_DIR)


@asset
def generar_datos_asset():
    """Ejecuta el script de generación de datos sintéticos."""
    _ensambrar_path()
    from generar_datos import generar_datos_minimercado

    generar_datos_minimercado()


@asset(deps=[generar_datos_asset])
def ingesta_dlt_asset():
    """Carga los CSVs hacia DuckDB usando dlt."""
    _ensambrar_path()
    from pipeline import run_pipeline

    run_pipeline()


@asset(deps=[ingesta_dlt_asset])
def dbt_transformations_asset():
    """Ejecuta dbt run y dbt test dentro de la carpeta dbt_project."""
    dbt_dir = os.path.join(ROOT_DIR, "dbt_project")
    subprocess.run(["dbt", "run"], cwd=dbt_dir, check=True)
    subprocess.run(["dbt", "test"], cwd=dbt_dir, check=True)


@asset(deps=[dbt_transformations_asset])
def reporte_calidad_asset():
    """Validación final post-transformación."""
    import duckdb

    db_path = os.path.join(ROOT_DIR, "data.duckdb")
    con = duckdb.connect(db_path)
    count = con.execute("SELECT COUNT(*) FROM main.mart_rentabilidad_productos").fetchone()[0]
    con.close()
    assert count > 0, "Error QA: El Mart de rentabilidad no contiene datos."


defs = Definitions(
    assets=[
        generar_datos_asset,
        ingesta_dlt_asset,
        dbt_transformations_asset,
        reporte_calidad_asset,
    ]
)
