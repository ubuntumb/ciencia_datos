"""Pruebas de ejercicio.py (tarea U1)."""

from datetime import date

import pytest
from ejercicio import (
    comision_esperada,
    descripcion_venta,
    parse_fecha,
    resumen_por_marca,
    separar_nombre_id,
)


def test_parse_fecha_formato_mes_dia_anio():
    assert parse_fecha("03/15/2024") == date(2024, 3, 15)


def test_parse_fecha_invalida_lanza_error():
    # Caso borde: el día 31 no existe en febrero.
    with pytest.raises(ValueError):
        parse_fecha("02/31/2024")


def test_separar_nombre_id_normal():
    assert separar_nombre_id("Juan Perez 1247") == ("Juan Perez", 1247)


def test_separar_nombre_id_sin_numero():
    # Caso borde: sin id al final, y con espacios sobrantes.
    assert separar_nombre_id("  Ana Pérez  ") == ("Ana Pérez", None)


def test_comision_esperada_redondea_a_dos_decimales():
    assert comision_esperada(19999.99, 0.035) == 700.0
    assert comision_esperada(0, 0.1) == 0


def test_resumen_por_marca_suma_por_marca():
    ventas = [
        {"car_make": "Ford", "sale_price": "100.5"},
        {"car_make": "Ford", "sale_price": "50"},
        {"car_make": "Toyota", "sale_price": "200"},
    ]
    assert resumen_por_marca(ventas) == {"Ford": 150.5, "Toyota": 200.0}


def test_resumen_por_marca_no_acumula_entre_llamadas():
    # Caso borde que detecta el bug del dict mutable por defecto (B006):
    # con acumulado={} la segunda llamada devolvía {"Ford": 200.0}.
    ventas = [{"car_make": "Ford", "sale_price": "100"}]
    resumen_por_marca(ventas)
    assert resumen_por_marca(ventas) == {"Ford": 100.0}


def test_resumen_por_marca_lista_vacia():
    assert resumen_por_marca([]) == {}


def test_descripcion_venta_con_precio_invalido_usa_cero():
    venta = {"car_make": "Ford", "car_model": "Focus", "sale_price": "no-es-numero"}
    assert descripcion_venta(venta) == "Venta registrada: Ford Focus por $0"
