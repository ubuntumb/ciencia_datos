"""Ejecuta el flujo en orden y comprueba el resultado desde Dagster."""

import os
from pathlib import Path

from dagster import Definitions, MaterializeResult, asset, define_asset_job

from analisis import construir_modelos, reporte_calidad
from generar_datos import RAIZ, generar_datos
from pipeline import cargar_datos


def carpeta_trabajo():
    return Path(os.environ.get("MINIMERCADO_RUN_DIR", str(RAIZ))).resolve()


@asset
def generar_datos_asset():
    conteos = generar_datos(carpeta_trabajo() / "data")
    return MaterializeResult(metadata=conteos)


@asset(deps=[generar_datos_asset])
def ingesta_dlt_asset():
    raiz = carpeta_trabajo()
    cargar_datos(raiz / "data", raiz / "data.duckdb")
    return MaterializeResult(metadata={"base": str(raiz / "data.duckdb")})


@asset(deps=[ingesta_dlt_asset])
def dbt_transformations_asset():
    construir_modelos(carpeta_trabajo() / "data.duckdb")


@asset(deps=[dbt_transformations_asset])
def reporte_calidad_asset():
    raiz = carpeta_trabajo()
    resumen = reporte_calidad(raiz / "data.duckdb")["resumen"]
    return MaterializeResult(
        metadata={
            "ventas": resumen["registros_venta"],
            "unidades": resumen["unidades"],
            "facturacion": str(resumen["facturacion"]),
            "reporte": str(raiz / "resultados.json"),
        }
    )


ASSETS = [generar_datos_asset, ingesta_dlt_asset, dbt_transformations_asset, reporte_calidad_asset]
defs = Definitions(assets=ASSETS, jobs=[define_asset_job("minimercado")])
