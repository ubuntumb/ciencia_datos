from pathlib import Path

import dagster as dg
from dagster_dbt import DbtCliResource
from dagster_duckdb import DuckDBResource
from orchestration.assets import (
    generar_datos_asset,
    ingesta_dlt_asset,
    marts_dbt,
    auditoria_calidad_asset,
    proyecto_dbt
)

ROOT = Path(__file__).resolve().parent.parent
CSV_PATH = ROOT / "data"

raw_data_job = dg.define_asset_job(
    name="raw_data",
    selection=dg.AssetSelection.keys("ingesta_dlt_asset")
)


@dg.sensor(job_name="raw_data", minimum_interval_seconds=60)
def nuevo_csv_sensor(context: dg.SensorEvaluationContext):
    for archivo in sorted(Path(CSV_PATH).glob("*.csv")):
        yield dg.RunRequest(
            run_key=archivo.name,
            tags={"archivo": archivo.name}
        )


defs = dg.Definitions(
    assets=[
        generar_datos_asset,
        ingesta_dlt_asset,
        marts_dbt,
        auditoria_calidad_asset,
    ],
    jobs=[
        raw_data_job
    ],
    sensors=[
        nuevo_csv_sensor
    ],
    resources={
        "dbt": DbtCliResource(project_dir=proyecto_dbt),
        "duckdb": DuckDBResource(database="minimarket.duckdb")
    }
)
