import dlt
import pandas as pd


@dlt.source
def minimercado_source():
    """Fuente de dlt que expone cada CSV como un recurso independiente."""
    tablas = [
        "productos",
        "vendedores",
        "compras",
        "ventas",
        "movimientos_stock",
    ]

    resources = []
    for tabla in tablas:
        df = pd.read_csv(f"data/{tabla}.csv")
        # Convertir a lista de diccionarios elimina la dependencia de pyarrow
        records = df.to_dict(orient="records")

        def make_generator(data_list):
            def generator():
                yield data_list

            return generator

        res = dlt.resource(
            make_generator(records),
            name=tabla,
            write_disposition="replace",
        )
        resources.append(res)

    return resources


def run_pipeline():
    """Ejecuta la ingesta a la base de datos DuckDB."""
    pipeline = dlt.pipeline(
        pipeline_name="minimercado_ingestion",
        destination="duckdb",
        dataset_name="main",
    )
    load_info = pipeline.run(minimercado_source(), credentials="data.duckdb")
    print(load_info)


if __name__ == "__main__":
    run_pipeline()
    print("Ingesta con dlt completada con éxito en 'data.duckdb'.")
