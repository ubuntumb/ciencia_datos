from datetime import date

from ejercicio import descripcion_venta, parse_fecha, resumen_por_marca, separar_nombre_id


def test_parse_fecha():
    """Convierte correctamente una fecha válida."""
    assert parse_fecha("10/12/2026") == date(2026, 10, 12)


def test_separar_nombre_id_sin_id():
    """Caso borde: texto sin identificador numérico."""
    assert separar_nombre_id("Jennifer Thomas") == ("Jennifer Thomas", None)


def test_resumen_por_marca_llamadas_independientes():
    """Caso borde: llamadas sucesivas no comparten memoria y operan con acumulado por defecto."""
    ventas_a = [{"car_make": "Toyota", "sale_price": "15000"}]
    ventas_b = [{"car_make": "Ford", "sale_price": "20000"}]

    res_a = resumen_por_marca(ventas_a)
    res_b = resumen_por_marca(ventas_b)

    assert res_a == {"Toyota": 15000.0}
    assert res_b == {"Ford": 20000.0}
    assert "Toyota" not in res_b


def test_descripcion_venta_precio_invalido():
    """Caso borde: captura de error de conversión de precio y uso de fallback."""
    venta = {
        "car_make": "Honda",
        "car_model": "Civic",
        "sale_price": "N/A",
    }
    assert descripcion_venta(venta) == "Venta registrada: Honda Civic por $0"
