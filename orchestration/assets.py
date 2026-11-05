from pathlib import Path

import duckdb
from dagster import RunRequest, SensorEvaluationContext, asset, AssetExecutionContext, AssetKey, sensor
from dagster_dbt import dbt_assets, DbtCliResource, DbtProject, DagsterDbtTranslator

proyecto_dbt = DbtProject(project_dir="transformador")
proyecto_dbt.prepare_if_dev()


class CustomDagsterDbtTranslator(DagsterDbtTranslator):
    def get_asset_key_for_source(self, dbt_resource_props):
        return AssetKey("ingesta_dlt_asset")


@asset(group_name="generacion")
def generar_datos_asset():
    """Generación de Datos Sintéticos con Semilla Fija"""
    from generador.seed import generar_dataset
    generar_dataset()
    return "CSVs generados en data/"


@asset(deps=[generar_datos_asset], group_name="ingesta")
def ingesta_dlt_asset():
    """Ingesta en DuckDB mediante dlt."""
    from ingestion.pipeline import ejecutar_ingesta
    ejecutar_ingesta()
    return "Tablas raw_data cargadas en DuckDB"


@dbt_assets(
    manifest=proyecto_dbt.manifest_path,
    dagster_dbt_translator=CustomDagsterDbtTranslator()
)
def marts_dbt(context: AssetExecutionContext, dbt: DbtCliResource):
    """Transformación dbt (Staging, Intermediate y Marts)."""

    yield from dbt.cli(["build"], context=context).stream()


@asset(deps=[marts_dbt], group_name="calidad")
def auditoria_calidad_asset(context: AssetExecutionContext):
    """Verificación de Aserciones."""

    con = duckdb.connect("minimarket.duckdb")
    cnt_ventas = con.execute(
        "SELECT COUNT(*) FROM raw_data.raw_ventas").fetchone()[0]
    cnt_dias = con.execute(
        "SELECT COUNT(*) FROM marts.mart_ventas_diarias").fetchone()[0]
    con.close()

    assert cnt_ventas == 600, f"Falla de auditoría: Se esperaban 600 ventas, encontradas {cnt_ventas}"
    assert cnt_dias == 90, f"Falla de auditoría: Se esperaban 90 días, encontrados {cnt_dias}"

    context.log.info("Auditoría validadas exitosamente.")
    return "Pipeline Aprobado"

