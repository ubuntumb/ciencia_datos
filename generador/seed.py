import os
import random
import pandas as pd
from datetime import datetime, timedelta

SEED = 2026


def generar_datos_producto(output_dir: str):
    # categorias de productos
    categorias = ["Lácteos", "Bebidas", "Abarrotes", "Limpieza", "Panadería"]
    productos = []

    for i in range(1, 11):
        cat = random.choice(categorias)
        costo = round(random.uniform(500, 350))
        precio = round(costo * random.uniform(1.25, 1.60))

        productos.append({
            "producto_id": i,
            "nombre_producto": f"Producto {i} ({cat[:3].upper()})",
            "categoria": cat,
            "costo_unitario": costo,
            "precio_venta": precio,
            "stock_inicial": random.randint(10, 200)
        })

    df_productos = pd.DataFrame(productos)
    df_productos.to_csv(f"{output_dir}/productos.csv", index=False, mode='w')

    return productos


def generar_datos_vendedore(output_dir: str):

    sucursales = ["Centro", "Norte", "Sur"]
    nombres = ["Marcos Benítez", "María Gómez",
               "Carlos López", "Ana Martínez", "Luis Rodríguez"]
    vendedores = []

    for i in range(1, 6):
        vendedores.append({
            "vendedor_id": i,
            "nombre_vendedor": nombres[i-1],
            "sucursal": random.choice(sucursales),
            "fecha_alta": (datetime(2024, 1, 1) + timedelta(days=random.randint(0, 180))).strftime("%Y-%m-%d")
        })

    df_vendedores = pd.DataFrame(vendedores)
    df_vendedores.to_csv(f"{output_dir}/vendedores.csv", index=False, mode='w')

    return vendedores


def generar_datos_compra(output_dir: str, productos):

    fecha_inicio = datetime(2024, 5, 3)
    proveedores = ["CESAR GUZMAN TODO MADERA SRL ", "GRANJA AVICOLA LA BLANCA SA", "MULTIENVASE S.A.", "SUPERMAS SA"]
    compras = []

    for i in range(1, 121):
        p = random.choice(productos)
        f_compra = fecha_inicio + timedelta(days=random.randint(0, 89))
        compras.append({
            "compra_id": i,
            "fecha_compra": f_compra.strftime("%Y-%m-%d"),
            "producto_id": p["producto_id"],
            "cantidad": random.randint(20, 100),
            "costo_unitario": p["costo_unitario"],
            "proveedor": random.choice(proveedores)
        })

    df_compras = pd.DataFrame(compras)
    df_compras.to_csv(f"{output_dir}/compras.csv", index=False, mode='w')


def generar_datos_venta(output_dir: str, productos, vendedores):

    fecha_inicio = datetime(2024, 5, 3)
    ventas = []

    for i in range(1, 601):
        p = random.choice(productos)
        v = random.choice(vendedores)
        f_venta = fecha_inicio + timedelta(days=random.randint(0, 89))
        cant = random.randint(1, 8)
        desc = round(p["precio_venta"] * cant * random.choice([0.0, 0.0, 0.05, 0.10]))
        ventas.append({
            "venta_id": i,
            "fecha_venta": f_venta.strftime("%Y-%m-%d %H:%M:%S"),
            "producto_id": p["producto_id"],
            "vendedor_id": v["vendedor_id"],
            "cantidad": cant,
            "precio_unitario": p["precio_venta"],
            "descuento": desc
        })
    df_ventas = pd.DataFrame(ventas)
    df_ventas.to_csv(f"{output_dir}/ventas.csv", index=False, mode='w')


def generar_datos_movimiento(output_dir: str):

    movimientos = []
    mov_id = 1
    df_compras = pd.read_csv(f"{output_dir}/compras.csv")
    df_ventas = pd.read_csv(f"{output_dir}/ventas.csv")
    
    for _, c in df_compras.iterrows():
        movimientos.append({
            "movimiento_id": mov_id,
            "fecha_movimiento": c["fecha_compra"],
            "producto_id": c["producto_id"],
            "tipo_movimiento": "ENTRADA_COMPRA",
            "cantidad": c["cantidad"]
        })
        mov_id += 1

    for _, v in df_ventas.iterrows():
        movimientos.append({
            "movimiento_id": mov_id,
            "fecha_movimiento": v["fecha_venta"][:10],
            "producto_id": v["producto_id"],
            "tipo_movimiento": "SALIDA_VENTA",
            "cantidad": -v["cantidad"]
        })
        mov_id += 1

    df_movimientos = pd.DataFrame(movimientos)
    df_movimientos.to_csv(f"{output_dir}/movimientos_stock.csv", index=False, mode='w')


def generar_dataset(output_dir: str = "data", seed: int = SEED):
    """ 
    Genera datos sinteticos utilizando un punto de partida y determinista para 90 días de operación 
    """
    random.seed(seed)
    os.makedirs(output_dir, exist_ok=True)
    
    productos = generar_datos_producto(output_dir)
    vendedores = generar_datos_vendedore(output_dir)
    generar_datos_compra(output_dir, productos)
    generar_datos_venta(output_dir, productos, vendedores)
    generar_datos_movimiento(output_dir)

    print("Los datos fueron generados!!!")



if __name__ == "__main__":
    generar_dataset()

