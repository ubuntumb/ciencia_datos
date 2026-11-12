import os
import random
from datetime import datetime, timedelta

import pandas as pd


def generar_datos_minimercado(seed: int = 42) -> None:
    """Genera un conjunto coherente de datos sintéticos con semilla fija."""
    random.seed(seed)
    os.makedirs("data", exist_ok=True)

    # 1. Productos (20 registros)
    categorias = ["Lácteos", "Bebidas", "Limpieza", "Snacks", "Abarrotes"]
    productos_data = []
    for i in range(1, 21):
        costo = round(random.uniform(5.0, 50.0), 2)
        precio = round(costo * random.uniform(1.2, 1.8), 2)
        productos_data.append(
            {
                "id": i,
                "nombre": f"Producto_{i}",
                "categoria": random.choice(categorias),
                "costo_unitario": costo,
                "precio_venta": precio,
                "stock_inicial": random.randint(50, 200),
            }
        )
    df_productos = pd.DataFrame(productos_data)
    df_productos.to_csv("data/productos.csv", index=False)

    # 2. Vendedores (5 registros)
    sucursales = ["Norte", "Centro", "Sur"]
    vendedores_data = []
    fecha_base = datetime(2025, 1, 1)
    for i in range(1, 6):
        vendedores_data.append(
            {
                "id": i,
                "nombre": f"Vendedor_{i}",
                "sucursal": random.choice(sucursales),
                "fecha_alta": (fecha_base - timedelta(days=random.randint(30, 300))).strftime(
                    "%Y-%m-%d"
                ),
            }
        )
    df_vendedores = pd.DataFrame(vendedores_data)
    df_vendedores.to_csv("data/vendedores.csv", index=False)

    # 3. Compras, Ventas y Movimientos de Stock (Mínimo 90 días de actividad)
    fecha_inicio = datetime(2025, 10, 1)
    compras_data, ventas_data, movimientos_data = [], [], []

    compra_id, venta_id, mov_id = 1, 1, 1

    for dia in range(90):
        fecha_actual = fecha_inicio + timedelta(days=dia)
        fecha_str = fecha_actual.strftime("%Y-%m-%d")

        # Compras (Reabastecimiento cada 3 días)
        if dia % 3 == 0:
            for _ in range(random.randint(3, 6)):
                prod = random.choice(productos_data)
                cant = random.randint(20, 50)
                compras_data.append(
                    {
                        "id": compra_id,
                        "fecha": fecha_str,
                        "producto_id": prod["id"],
                        "cantidad": cant,
                        "costo_unitario": prod["costo_unitario"],
                        "proveedor": f"Proveedor_{random.randint(1, 3)}",
                    }
                )
                movimientos_data.append(
                    {
                        "id": mov_id,
                        "fecha": fecha_str,
                        "producto_id": prod["id"],
                        "tipo_movimiento": "ENTRADA",
                        "cantidad": cant,
                    }
                )
                mov_id += 1
                compra_id += 1

        # Ventas diarias
        for _ in range(random.randint(6, 12)):
            prod = random.choice(productos_data)
            cant = random.randint(1, 5)
            descuento = round(random.choice([0.0, 0.05, 0.10]), 2)
            ventas_data.append(
                {
                    "id": venta_id,
                    "fecha": fecha_str,
                    "producto_id": prod["id"],
                    "cantidad": cant,
                    "precio_unitario": prod["precio_venta"],
                    "descuento": descuento,
                    "vendedor_id": random.randint(1, 5),
                }
            )
            movimientos_data.append(
                {
                    "id": mov_id,
                    "fecha": fecha_str,
                    "producto_id": prod["id"],
                    "tipo_movimiento": "SALIDA",
                    "cantidad": cant,
                }
            )
            mov_id += 1
            venta_id += 1

    pd.DataFrame(compras_data).to_csv("data/compras.csv", index=False)
    pd.DataFrame(ventas_data).to_csv("data/ventas.csv", index=False)
    pd.DataFrame(movimientos_data).to_csv("data/movimientos_stock.csv", index=False)


if __name__ == "__main__":
    generar_datos_minimercado()
    print("Datos sintéticos generados en la carpeta 'data/'.")
