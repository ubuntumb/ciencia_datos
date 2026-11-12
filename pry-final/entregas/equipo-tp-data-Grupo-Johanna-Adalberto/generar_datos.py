"""Genera datos ficticios de un minimercado, con compras y ventas conciliadas."""

import argparse
import csv
import random
from datetime import date, timedelta
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
SEMILLA = 42
DIAS = 90
INICIO = date(2026, 1, 1)
CATALOGO = {
    "Almacén": ("Arroz", "Fideos", "Harina", "Aceite", "Azúcar"),
    "Bebidas": ("Agua", "Jugo", "Gaseosa", "Yerba mate", "Café"),
    "Limpieza": ("Jabón", "Detergente", "Lavandina", "Esponja", "Papel higiénico"),
    "Refrigerados": ("Leche", "Yogur", "Queso", "Manteca", "Huevos"),
}
DESCUENTOS = ("0.00", "0.00", "0.00", "0.05", "0.10")


def guardar_csv(ruta, filas):
    """Preserva el orden de columnas y filas para obtener archivos repetibles."""
    with ruta.open("w", encoding="utf-8", newline="") as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=tuple(filas[0]))
        escritor.writeheader()
        escritor.writerows(filas)


def generar_datos(carpeta=RAIZ / "data", semilla=SEMILLA):
    """Devuelve los conteos de cinco CSV para un período fijo de 90 días."""
    carpeta = Path(carpeta)
    carpeta.mkdir(parents=True, exist_ok=True)
    rng = random.Random(semilla)
    productos = []
    for categoria, nombres in CATALOGO.items():
        for nombre in nombres:
            pid = len(productos) + 1
            costo = rng.randrange(1500, 12001, 500)
            productos.append(
                dict(
                    id=pid,
                    nombre=nombre,
                    categoria=categoria,
                    costo_unitario=costo,
                    precio_venta=costo + rng.randrange(1000, 3501, 500),
                    stock_inicial=rng.randint(15, 25),
                )
            )
    vendedores = [
        dict(id=i, nombre=f"Vendedor {i:02}", sucursal="Central", fecha_alta="2025-12-01")
        for i in range(1, 6)
    ]
    compras, ventas, movimientos = [], [], []
    stock = {p["id"]: p["stock_inicial"] for p in productos}
    popularidad = [21 - p["id"] for p in productos]

    def registrar_movimiento(fecha, pid, tipo, cantidad, referencia):
        movimientos.append(
            dict(
                id=len(movimientos) + 1,
                fecha=fecha,
                producto_id=pid,
                tipo=tipo,
                cantidad=cantidad,
                referencia_id=referencia,
            )
        )
        stock[pid] += cantidad if tipo == "entrada" else -cantidad

    def comprar(fecha, producto, cantidad):
        pid = producto["id"]
        referencia = len(compras) + 1
        compras.append(
            dict(
                id=referencia,
                fecha=fecha,
                producto_id=pid,
                cantidad=cantidad,
                costo_unitario=producto["costo_unitario"] + rng.choice((-200, 0, 200)),
                proveedor=f"Proveedor {1 + (pid - 1) % 4}",
            )
        )
        registrar_movimiento(fecha, pid, "entrada", cantidad, referencia)

    for desplazamiento in range(DIAS):
        dia = INICIO + timedelta(days=desplazamiento)
        fecha = dia.isoformat()
        # La reposición favorece los artículos con menor stock.
        for _ in range(2):
            producto = rng.choices(
                productos, weights=[1 / (stock[p["id"]] + 1) for p in productos]
            )[0]
            comprar(fecha, producto, rng.randint(8, 18))

        fin_de_semana = dia.weekday() >= 5
        for _ in range(rng.randint(6, 10) + 3 * fin_de_semana):
            producto = rng.choices(productos, weights=popularidad)[0]
            pid = producto["id"]
            cantidad = rng.randint(1, 4 if fin_de_semana else 3)
            if stock[pid] < cantidad:
                comprar(fecha, producto, rng.randint(12, 20))
            referencia = len(ventas) + 1
            ventas.append(
                dict(
                    id=referencia,
                    fecha=fecha,
                    producto_id=pid,
                    cantidad=cantidad,
                    precio_unitario=producto["precio_venta"],
                    descuento=rng.choice(DESCUENTOS),
                    vendedor_id=rng.randint(1, 5),
                )
            )
            registrar_movimiento(fecha, pid, "salida", cantidad, referencia)

    tablas = dict(
        productos=productos,
        vendedores=vendedores,
        compras=compras,
        ventas=ventas,
        movimientos_stock=movimientos,
    )
    for nombre, filas in tablas.items():
        guardar_csv(carpeta / f"{nombre}.csv", filas)
    return {nombre: len(filas) for nombre, filas in tablas.items()}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--semilla", type=int, default=SEMILLA)
    parser.add_argument("--carpeta", type=Path, default=RAIZ / "data")
    args = parser.parse_args()
    print(generar_datos(args.carpeta, args.semilla))
