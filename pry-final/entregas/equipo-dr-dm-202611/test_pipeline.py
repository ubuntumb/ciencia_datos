import pytest
import os
import duckdb
import pandas as pd
import generar_datos
from orchestration.definitions import defs


def test_reproducibilidad_generar_datos():
    """
    1. Generación y Consistencia: Valida la reproducibilidad sintética
    invocando generar_datos_minimercado y verificando la integridad de ventas.csv.
    """
    if hasattr(generar_datos, "generar_datos_minimercado"):
        generar_datos.generar_datos_minimercado()
    else:
        generar_datos.main()

    archivo_ventas = os.path.join("data", "ventas.csv")
    assert os.path.exists(archivo_ventas), "El archivo ventas.csv no fue creado en 'data/'."

    df_ventas = pd.read_csv(archivo_ventas)
    assert len(df_ventas) >= 500, "El volumen sintético de ventas es menor al esperado."

    # Validación de esquema de datos sintéticos primarios
    columnas_esperadas = ["id", "fecha", "producto_id", "cantidad", "precio_unitario"]
    for col in columnas_esperadas:
        assert col in df_ventas.columns, f"Falta la columna '{col}' en ventas.csv."

    assert df_ventas["precio_unitario"].isnull().sum() == 0, "Existen valores nulos en precio_unitario."


def test_esquema_duckdb():
    """
    2. Ingesta (dlt + DuckDB): Valida la existencia y persistencia de las tablas
    crudas ingestadas por dlt en la base relacional local data.duckdb.
    """
    db_path = "data.duckdb"
    assert os.path.exists(db_path), f"La base de datos {db_path} no existe."

    conn = duckdb.connect(db_path)
    tablas = [row[0] for row in conn.execute("SHOW TABLES").fetchall()]
    conn.close()

    tablas_esperadas = ["ventas", "productos", "compras", "vendedores", "movimientos_stock"]
    for tabla in tablas_esperadas:
        assert tabla in tablas, f"La tabla cruda '{tabla}' no fue encontrada en DuckDB."


def test_rentabilidad_y_clasificacion_abc():
    """
    3. Análisis y Métricas (dbt): Valida la existencia del modelo analítico de
    rentabilidad y la estructura de clasificación ABC en DuckDB.
    """
    db_path = "data.duckdb"
    assert os.path.exists(db_path), f"La base de datos {db_path} no existe."

    conn = duckdb.connect(db_path)
    # Buscar tabla/vista en cualquier esquema de la base de datos
    tablas_df = conn.execute("SELECT table_name FROM information_schema.tables").df()
    lista_tablas = tablas_df["table_name"].tolist() if not tablas_df.empty else []

    assert "mart_rentabilidad_productos" in lista_tablas, (
        "La tabla 'mart_rentabilidad_productos' no fue encontrada en DuckDB. "
        "Asegúrate de ejecutar 'dbt run' antes de lanzar pytest."
    )

    df_mart = conn.execute("SELECT * FROM mart_rentabilidad_productos").df()
    conn.close()

    assert not df_mart.empty, "La tabla mart_rentabilidad_productos está vacía."
    assert "clasificacion_abc" in df_mart.columns, "Falta la columna clasificacion_abc."

    valores_abc = set(df_mart["clasificacion_abc"].dropna().unique())
    assert valores_abc.issubset({"A", "B", "C"}), f"Clasificación ABC contiene valores no válidos: {valores_abc}"


def test_metricas_ventas_diarias():
    """
    4. Análisis y Métricas (dbt): Valida la integridad del resumen diario
    y la presencia de métricas analíticas en mart_ventas_diarias.
    """
    db_path = "data.duckdb"
    assert os.path.exists(db_path), f"La base de datos {db_path} no existe."

    conn = duckdb.connect(db_path)
    tablas_df = conn.execute("SELECT table_name FROM information_schema.tables").df()
    lista_tablas = tablas_df["table_name"].tolist() if not tablas_df.empty else []

    assert "mart_ventas_diarias" in lista_tablas, (
        "La tabla 'mart_ventas_diarias' no fue encontrada en DuckDB. "
        "Asegúrate de ejecutar 'dbt run' antes de lanzar pytest."
    )

    df_diarias = conn.execute("SELECT * FROM mart_ventas_diarias").df()
    conn.close()

    assert not df_diarias.empty, "La tabla mart_ventas_diarias está vacía."
    assert "fecha" in df_diarias.columns, "Falta la columna fecha en mart_ventas_diarias."


def test_orquestacion_dagster_assets():
    """
    5. Orquestación (Dagster): Valida que las definiciones de Software-Defined Assets
    estén cargadas correctamente en el proyecto.
    """
    assets = list(defs.assets) if defs.assets else []

    nombres_assets = []
    for asset in assets:
        if hasattr(asset, "key"):
            nombres_assets.append(asset.key.to_user_string())
        elif hasattr(asset, "keys"):
            nombres_assets.extend([k.to_user_string() for k in asset.keys])

    assert len(nombres_assets) >= 3, "El repositorio de Dagster contiene menos de 3 activos configurados."
    assert any("generar_datos" in a for a in nombres_assets), "Falta el activo de generación de datos en Dagster."
    assert any("ingesta" in a or "dlt" in a for a in nombres_assets), "Falta el activo de ingesta dlt en Dagster."