"""Comprueba determinismo, persistencia y conciliación de extremo a extremo."""

import csv
import json
from decimal import Decimal

import duckdb
from dagster import materialize

from generar_datos import generar_datos
from orchestration.definitions import ASSETS
from pipeline import COLUMNAS, cargar_datos


def test_generacion_reproducible(tmp_path):
    primera, segunda = tmp_path / "primera", tmp_path / "segunda"
    conteos = generar_datos(primera)
    assert generar_datos(segunda) == conteos
    assert conteos["productos"] == 20 and conteos["vendedores"] == 5
    assert conteos["compras"] >= 100 and conteos["ventas"] >= 500
    assert conteos["movimientos_stock"] == conteos["compras"] + conteos["ventas"]
    for nombre in COLUMNAS:
        ruta = f"{nombre}.csv"
        assert (primera / ruta).read_bytes() == (segunda / ruta).read_bytes()


def test_ingesta_tipificada_e_idempotente(tmp_path):
    carpeta, base = tmp_path / "data", tmp_path / "data.duckdb"
    conteos = generar_datos(carpeta)

    def verificar_y_leer():
        with duckdb.connect(str(base), read_only=True) as db:
            esquema = dict(
                db.execute(
                    "select column_name, data_type from information_schema.columns "
                    "where table_schema = 'raw' and table_name = 'ventas'"
                ).fetchall()
            )
            assert esquema["fecha"] == "DATE"
            assert esquema["cantidad"] == "BIGINT"
            assert esquema["descuento"].startswith("DECIMAL")
            for tabla, esperado in conteos.items():
                assert db.execute(
                    f"select count(*), count(distinct id) from raw.{tabla}"
                ).fetchone() == (esperado, esperado)
            campos = ", ".join(COLUMNAS["ventas"])
            return db.execute(f"select {campos} from raw.ventas order by id").fetchall()

    cargar_datos(carpeta, base)
    primera = verificar_y_leer()
    cargar_datos(carpeta, base)
    assert verificar_y_leer() == primera


def test_dagster_de_punta_a_punta(tmp_path, monkeypatch):
    monkeypatch.setenv("MINIMERCADO_RUN_DIR", str(tmp_path))
    corrida = materialize(ASSETS)
    assert corrida.success
    resultados = json.loads((tmp_path / "resultados.json").read_text(encoding="utf-8"))
    with (tmp_path / "data" / "ventas.csv").open(encoding="utf-8", newline="") as archivo:
        ventas = list(csv.DictReader(archivo))
    facturacion = sum(
        int(v["cantidad"]) * Decimal(v["precio_unitario"]) * (1 - Decimal(v["descuento"]))
        for v in ventas
    )
    assert resultados["resumen"]["dias"] == len({v["fecha"] for v in ventas}) == 90
    assert resultados["resumen"]["registros_venta"] == len(ventas)
    assert Decimal(resultados["resumen"]["facturacion"]) == facturacion
    assert sum(fila["unidades"] for fila in resultados["abc"]) == sum(
        int(v["cantidad"]) for v in ventas
    )
    assert all(fila["stock_final"] >= 0 for fila in resultados["inventario"])
    assert resultados["controles"]["saldos_negativos"] == 0
