from datetime import date

from ejercicio import parse_fecha, resumen_por_marca


def test_parse_fecha():
    assert parse_fecha("03/14/2026") == date(2026, 3, 14)


def test_resumen_por_marca_no_comparte():
    primero = resumen_por_marca([{"car_make": "Toyota", "sale_price": 1000}])
    segundo = resumen_por_marca([{"car_make": "Honda", "sale_price": 2000}])
    assert primero == {"Toyota": 1000}
    assert segundo == {"Honda": 2000}
