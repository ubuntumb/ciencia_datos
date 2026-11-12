"""Ejecuta las consultas de análisis de dbt_project/analyses sobre data.duckdb.

Uso (después de dbt build): python consultas.py
"""

from pathlib import Path

import duckdb

CARPETA = Path(__file__).resolve().parent
RUTA_BD = CARPETA / "data.duckdb"
CARPETA_ANALISIS = CARPETA / "dbt_project" / "analyses"


def ejecutar(ruta_sql: Path, ruta_bd: Path = RUTA_BD) -> tuple[list[str], list[tuple]]:
    """Ejecuta un archivo SQL y devuelve los nombres de columna y las filas."""
    with duckdb.connect(str(ruta_bd), read_only=True) as conexion:
        cursor = conexion.execute(ruta_sql.read_text(encoding="utf-8"))
        columnas = [c[0] for c in cursor.description]
        return columnas, cursor.fetchall()


def main() -> None:
    for ruta_sql in sorted(CARPETA_ANALISIS.glob("*.sql")):
        columnas, filas = ejecutar(ruta_sql)
        print(f"\n=== {ruta_sql.stem} ===")
        print(" | ".join(columnas))
        for fila in filas:
            print(" | ".join(str(valor) for valor in fila))


if __name__ == "__main__":
    main()
