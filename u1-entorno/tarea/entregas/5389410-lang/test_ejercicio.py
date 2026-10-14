from datetime import date

from ejercicio import comision_esperada, parse_fecha, resumen_por_marca, separar_nombre_id


def test_parse_fecha_convierte_texto_en_fecha():
    assert parse_fecha("03/15/2022") == date(2022, 3, 15)


def test_separar_nombre_id_sin_numero():
    # Caso borde: el texto no termina en un número, así que el id es None.
    assert separar_nombre_id("Jennifer Thomas") == ("Jennifer Thomas", None)


def test_comision_esperada_redondea_a_dos_decimales():
    assert comision_esperada(1000, 0.0333) == 33.3


def test_resumen_por_marca_no_acumula_entre_llamadas():
    # Caso borde: llamar dos veces no debe mezclar los resultados.
    ventas = [{"car_make": "Ford", "sale_price": "100"}]
    resumen_por_marca(ventas)
    assert resumen_por_marca(ventas) == {"Ford": 100.0}