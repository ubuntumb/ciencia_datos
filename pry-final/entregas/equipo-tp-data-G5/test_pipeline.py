"""Pruebas del pipeline del minimercado: generación, ingesta y flujo completo."""

import csv
from datetime import date

import duckdb
import generar_datos
import pipeline
import pytest
from orchestration.definitions import correr_dbt, defs, revisar_calidad

TABLAS = ["productos", "vendedores", "compras", "ventas", "movimientos_stock"]


def leer(carpeta, tabla: str) -> list[dict]:
    with (carpeta / f"{tabla}.csv").open(encoding="utf-8") as archivo:
        return list(csv.DictReader(archivo))


@pytest.fixture
def entorno(tmp_path, monkeypatch):
    """Carpeta de datos y base DuckDB temporales, para no tocar los archivos reales."""
    monkeypatch.setenv("DLT_DATA_DIR", str(tmp_path / ".dlt"))
    carpeta = tmp_path / "data"
    generar_datos.generar(carpeta=carpeta)
    return carpeta, tmp_path / "data.duckdb"


def test_generacion_reproducible(tmp_path):
    """Con la misma semilla los CSV salen idénticos; con otra semilla, distintos."""
    a, b, c = tmp_path / "a", tmp_path / "b", tmp_path / "c"
    generar_datos.generar(semilla=42, carpeta=a)
    generar_datos.generar(semilla=42, carpeta=b)
    generar_datos.generar(semilla=7, carpeta=c)

    for tabla in TABLAS:
        assert (a / f"{tabla}.csv").read_bytes() == (b / f"{tabla}.csv").read_bytes()
    assert (a / "ventas.csv").read_bytes() != (c / "ventas.csv").read_bytes()


def test_datos_cumplen_minimos_y_claves(entorno):
    """Volúmenes mínimos, 90 días o más, claves válidas e importes positivos."""
    carpeta, _ = entorno
    datos = {tabla: leer(carpeta, tabla) for tabla in TABLAS}

    assert len(datos["productos"]) == 20
    assert len(datos["vendedores"]) == 5
    assert len(datos["compras"]) >= 100
    assert len(datos["ventas"]) >= 500

    fechas = [date.fromisoformat(v["fecha"]) for v in datos["ventas"]]
    assert (max(fechas) - min(fechas)).days + 1 >= 90

    productos = {p["id"] for p in datos["productos"]}
    vendedores = {v["id"] for v in datos["vendedores"]}
    assert all(v["producto_id"] in productos for v in datos["ventas"])
    assert all(v["vendedor_id"] in vendedores for v in datos["ventas"])
    assert all(c["producto_id"] in productos for c in datos["compras"])
    assert all(int(v["cantidad"]) > 0 and float(v["precio_unitario"]) > 0 for v in datos["ventas"])
    assert all(int(c["cantidad"]) > 0 and float(c["costo_unitario"]) > 0 for c in datos["compras"])


def test_esquema_duckdb_tras_ingesta(entorno):
    """Después de dlt existen las 5 tablas en el esquema raw con sus columnas."""
    carpeta, ruta_bd = entorno
    pipeline.cargar(ruta_bd, carpeta)

    with duckdb.connect(str(ruta_bd), read_only=True) as con:
        tablas = {
            fila[0]
            for fila in con.execute(
                "select table_name from information_schema.tables where table_schema = 'raw'"
            ).fetchall()
        }
        columnas = {fila[0] for fila in con.execute("describe raw.ventas").fetchall()}

    assert set(TABLAS) <= tablas
    assert {"id", "fecha", "producto_id", "cantidad", "precio_unitario", "descuento"} <= columnas
    assert "vendedor_id" in columnas


def test_ingesta_idempotente(entorno):
    """Ejecutar la ingesta dos veces no duplica registros."""
    carpeta, ruta_bd = entorno
    pipeline.cargar(ruta_bd, carpeta)
    pipeline.cargar(ruta_bd, carpeta)

    with duckdb.connect(str(ruta_bd), read_only=True) as con:
        for tabla in TABLAS:
            total, distintos = con.execute(
                f"select count(*), count(distinct id) from raw.{tabla}"
            ).fetchone()
            assert total == distintos == len(leer(carpeta, tabla))


def test_flujo_completo_de_punta_a_punta(entorno):
    """Genera, ingesta, corre dbt (modelos y pruebas) y pasa todos los controles finales."""
    carpeta, ruta_bd = entorno
    pipeline.cargar(ruta_bd, carpeta)

    correr_dbt(ruta_bd)

    controles = revisar_calidad(ruta_bd)
    assert all(controles.values()), controles
    with duckdb.connect(str(ruta_bd), read_only=True) as con:
        clases = {
            fila[0]
            for fila in con.execute(
                "select distinct clase_abc from marts.mart_clasificacion_abc"
            ).fetchall()
        }
    assert clases == {"A", "B", "C"}


def test_dagster_encadena_cuatro_assets_en_orden():
    """El grafo de Dagster tiene los cuatro assets y cada uno depende del anterior."""
    dependencias = {
        spec.key.to_user_string(): {d.asset_key.to_user_string() for d in spec.deps}
        for spec in defs.resolve_all_asset_specs()
    }
    assert dependencias == {
        "generar_datos_asset": set(),
        "ingesta_dlt_asset": {"generar_datos_asset"},
        "dbt_transformations_asset": {"ingesta_dlt_asset"},
        "reporte_calidad_asset": {"dbt_transformations_asset"},
    }
