"""Orquestación del pipeline del minimercado con Dagster.

Cuatro assets encadenados: generar datos -> ingesta dlt -> dbt build -> reporte de calidad.
Desde la carpeta del equipo:
    dagster dev -f orchestration/definitions.py                              # interfaz web
    dagster job execute -f orchestration/definitions.py -j pipeline_completo  # línea de comandos
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

import dagster as dg
import duckdb
import generar_datos
import pipeline

CARPETA = Path(__file__).resolve().parent.parent
CARPETA_DBT = CARPETA / "dbt_project"
RUTA_BD = CARPETA / "data.duckdb"


def correr_dbt(ruta_bd: Path = RUTA_BD) -> str:
    """Ejecuta dbt build (modelos y pruebas) en un proceso aparte; falla si algo no pasa.

    Se usa un proceso aparte para que dbt cierre su conexión a DuckDB al terminar.
    """
    dbt = Path(sys.executable).with_name("dbt")
    comando = [str(dbt) if dbt.exists() else shutil.which("dbt") or "dbt", "build"]
    comando += ["--project-dir", str(CARPETA_DBT), "--profiles-dir", str(CARPETA_DBT)]
    entorno = {**os.environ, "DUCKDB_PATH": str(ruta_bd)}
    resultado = subprocess.run(comando, env=entorno, capture_output=True, text=True)
    if resultado.returncode != 0:
        raise dg.Failure(f"dbt build falló:\n{resultado.stdout[-3000:]}")
    return resultado.stdout


# Controles finales: cada consulta devuelve verdadero si el control pasa.
CONTROLES = {
    "90_dias_o_mas_de_ventas": "select count(*) >= 90 from marts.mart_ventas_diarias",
    "20_productos_en_rentabilidad": "select count(*) = 20 from marts.mart_rentabilidad_productos",
    "5_vendedores_en_desempeno": "select count(*) = 5 from marts.mart_desempeno_vendedores",
    "ventas_sin_duplicados": "select count(*) = count(distinct id) from raw.ventas",
    "facturacion_cuadra_con_ventas": (
        "select abs((select sum(facturacion_neta) from marts.mart_ventas_diarias)"
        " - (select sum(importe_neto) from staging.stg_ventas)) < 1"
    ),
    "abc_suma_100": (
        "select abs(sum(participacion_pct) - 100) < 0.1 from marts.mart_clasificacion_abc"
    ),
}


def revisar_calidad(ruta_bd: Path = RUTA_BD) -> dict[str, bool]:
    """Ejecuta los controles finales sobre la base y dice cuáles pasaron."""
    with duckdb.connect(str(ruta_bd), read_only=True) as con:
        return {nombre: bool(con.execute(sql).fetchone()[0]) for nombre, sql in CONTROLES.items()}


@dg.asset(group_name="minimercado")
def generar_datos_asset() -> dg.MaterializeResult:
    """Genera los CSV sintéticos en data/ con semilla fija."""
    conteos = generar_datos.generar()
    return dg.MaterializeResult(metadata=conteos)


@dg.asset(group_name="minimercado", deps=[generar_datos_asset])
def ingesta_dlt_asset() -> dg.MaterializeResult:
    """Carga los CSV en data.duckdb (esquema raw) con dlt, sin duplicar."""
    info = pipeline.cargar()
    return dg.MaterializeResult(metadata={"paquetes_cargados": len(info.loads_ids)})


@dg.asset(group_name="minimercado", deps=[ingesta_dlt_asset])
def dbt_transformations_asset(context: dg.AssetExecutionContext) -> None:
    """Construye staging, intermediate y marts, y corre las pruebas de dbt."""
    salida = correr_dbt()
    context.log.info(salida.strip().splitlines()[-1])


@dg.asset(group_name="minimercado", deps=[dbt_transformations_asset])
def reporte_calidad_asset() -> dg.MaterializeResult:
    """Valida la salida final; falla si algún control no se cumple."""
    controles = revisar_calidad()
    fallidos = [nombre for nombre, ok in controles.items() if not ok]
    if fallidos:
        raise dg.Failure(f"Controles de calidad fallidos: {', '.join(fallidos)}")
    return dg.MaterializeResult(metadata=controles)


pipeline_completo = dg.define_asset_job("pipeline_completo", selection="*")

defs = dg.Definitions(
    assets=[
        generar_datos_asset,
        ingesta_dlt_asset,
        dbt_transformations_asset,
        reporte_calidad_asset,
    ],
    jobs=[pipeline_completo],
)
