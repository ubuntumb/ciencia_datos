"""Ejecuta dbt y consolida los indicadores comprobados en resultados.json."""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import duckdb

from generar_datos import RAIZ


def construir_modelos(base):
    base = Path(base).resolve()
    proyecto = RAIZ / "dbt_project"
    ejecutable = Path(sys.executable).with_name("dbt.exe" if os.name == "nt" else "dbt")
    dbt = str(ejecutable) if ejecutable.is_file() else shutil.which("dbt")
    if dbt is None:
        raise RuntimeError("No se encontró dbt en el entorno del proyecto")
    env = os.environ | {
        "MINIMERCADO_DB": str(base),
        "DBT_SEND_ANONYMOUS_USAGE_STATS": "false",
    }
    subprocess.run(
        [
            dbt,
            "build",
            "--project-dir",
            str(proyecto),
            "--profiles-dir",
            str(proyecto),
            "--target-path",
            str(base.parent / "target"),
            "--log-path",
            str(base.parent / "logs"),
        ],
        check=True,
        env=env,
    )


def consultar(conexion, sql):
    consulta = conexion.execute(sql)
    columnas = [columna[0] for columna in consulta.description]
    return [dict(zip(columnas, fila, strict=True)) for fila in consulta.fetchall()]


def reporte_calidad(base):
    base = Path(base).resolve()
    with duckdb.connect(str(base), read_only=True) as conexion:
        resumen = consultar(
            conexion,
            """
            select count(*) as dias, sum(registros_venta) as registros_venta,
                sum(unidades) as unidades, sum(facturacion) as facturacion,
                round(avg(facturacion), 2) as promedio_diario,
                round(median(facturacion), 2) as mediana_diaria,
                round(stddev_pop(facturacion), 2) as desviacion_diaria
            from analytics.mart_ventas_diarias
        """,
        )[0]
        controles = consultar(
            conexion,
            """
            select
                (select count(*) from raw.ventas) as ventas_origen,
                (select sum(facturacion) from analytics.mart_desempeno_vendedores)
                    as facturacion_vendedores,
                (select sum(facturacion) from analytics.mart_rentabilidad_productos)
                    as facturacion_productos,
                (select count(*) from analytics.int_movimientos_stock where saldo_stock < 0)
                    as saldos_negativos,
                (select count(*) from raw.compras) as compras,
                (select count(*) from raw.productos) as productos,
                (select count(*) from raw.vendedores) as vendedores
        """,
        )[0]
        if (
            resumen["dias"] < 90
            or controles["ventas_origen"] < 500
            or controles["compras"] < 100
            or controles["productos"] != 20
            or controles["vendedores"] != 5
            or resumen["registros_venta"] != controles["ventas_origen"]
            or resumen["facturacion"] != controles["facturacion_vendedores"]
            or resumen["facturacion"] != controles["facturacion_productos"]
            or controles["saldos_negativos"]
        ):
            raise ValueError(f"No se conciliaron las salidas: {resumen}; {controles}")
        resultados = {
            "resumen": resumen,
            "controles": controles,
            "vendedores": consultar(
                conexion,
                """
                select * from analytics.mart_desempeno_vendedores
                order by facturacion desc, vendedor_id
            """,
            ),
            "rentabilidad": consultar(
                conexion,
                """
                select * from analytics.mart_rentabilidad_productos
                order by ganancia_bruta desc, producto_id
            """,
            ),
            "inventario": consultar(
                conexion,
                """
                select producto_id, nombre, stock_final, round(rotacion, 2) as rotacion,
                    round(dias_disponibles, 2) as dias_disponibles, punto_reposicion, reponer
                from analytics.mart_rotacion_inventario order by producto_id
            """,
            ),
            "abc": consultar(
                conexion,
                """
                select clase, count(*) as productos, sum(unidades) as unidades,
                    sum(facturacion) as facturacion
                from analytics.mart_abc_productos group by clase order by clase
            """,
            ),
        }
    (base.parent / "resultados.json").write_text(
        json.dumps(resultados, indent=2, default=str, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return resultados


if __name__ == "__main__":
    base = RAIZ / "data.duckdb"
    construir_modelos(base)
    print(reporte_calidad(base)["resumen"])
