"""Genera los datos sintéticos de un minimercado (92 días) en archivos CSV.

Con la misma semilla siempre produce exactamente los mismos archivos.
Uso: python generar_datos.py
"""

import csv
import random
from datetime import date, timedelta
from pathlib import Path

SEMILLA = 42
CARPETA_DATOS = Path(__file__).resolve().parent / "data"
FECHA_INICIO = date(2026, 7, 1)
DIAS = 92  # 1 de julio al 30 de septiembre de 2026
DIAS_DE_REPOSICION = {0, 3}  # lunes y jueves llega el pedido a los proveedores

# (nombre, categoría, costo unitario en Gs., precio de venta en Gs., ventas diarias esperadas)
CATALOGO = [
    ("Arroz 1 kg", "Almacén", 6_500, 9_000, 9),
    ("Fideo tallarín 500 g", "Almacén", 4_200, 6_000, 8),
    ("Aceite de girasol 900 ml", "Almacén", 11_000, 15_000, 5),
    ("Yerba mate 500 g", "Almacén", 9_500, 13_500, 10),
    ("Azúcar 1 kg", "Almacén", 5_800, 8_000, 7),
    ("Harina de trigo 1 kg", "Almacén", 4_800, 6_800, 5),
    ("Café molido 250 g", "Almacén", 14_500, 21_000, 2),
    ("Leche entera 1 L", "Lácteos", 5_200, 7_000, 12),
    ("Queso Paraguay 500 g", "Lácteos", 19_000, 27_000, 3),
    ("Yogur bebible 1 L", "Lácteos", 8_000, 11_500, 4),
    ("Pan lactal 500 g", "Panadería", 9_000, 13_000, 6),
    ("Chipa 250 g", "Panadería", 6_000, 10_000, 8),
    ("Galletitas dulces 300 g", "Panadería", 5_500, 8_500, 5),
    ("Agua mineral 2 L", "Bebidas", 4_000, 6_500, 11),
    ("Gaseosa cola 2 L", "Bebidas", 9_000, 13_000, 9),
    ("Jugo de naranja 1 L", "Bebidas", 7_500, 11_000, 3),
    ("Huevos (docena)", "Frescos", 14_000, 19_000, 6),
    ("Detergente 750 ml", "Limpieza", 8_500, 12_500, 2),
    ("Jabón en polvo 800 g", "Limpieza", 16_000, 23_000, 1),
    ("Papel higiénico x4", "Limpieza", 10_500, 15_000, 4),
]

PROVEEDORES = {
    "Almacén": "Distribuidora Central",
    "Lácteos": "Lácteos del Sur",
    "Panadería": "Panificadora San José",
    "Bebidas": "Bebidas del Paraguay",
    "Frescos": "Granja La Esperanza",
    "Limpieza": "Limpia Hogar S.A.",
}

VENDEDORES = [
    ("Ana Benítez", "Centro", date(2023, 3, 1)),
    ("Carlos Giménez", "Centro", date(2024, 1, 15)),
    ("Lucía Ortiz", "Barrio Obrero", date(2022, 8, 10)),
    ("Diego Ramírez", "Barrio Obrero", date(2025, 5, 2)),
    ("Sofía Cáceres", "Centro", date(2026, 2, 20)),
]

# Sábado y domingo se vende más; el lunes, menos.
FACTOR_DIA_SEMANA = [0.85, 0.95, 1.0, 1.0, 1.1, 1.35, 1.2]


def _escribir_csv(ruta: Path, filas: list[dict]) -> None:
    """Guarda una lista de diccionarios como CSV (las columnas salen de la primera fila)."""
    with ruta.open("w", newline="", encoding="utf-8") as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=list(filas[0]))
        escritor.writeheader()
        escritor.writerows(filas)


def generar(semilla: int = SEMILLA, carpeta: Path = CARPETA_DATOS) -> dict[str, int]:
    """Simula 92 días del minimercado y escribe un CSV por entidad.

    Devuelve cuántos registros quedaron en cada archivo.
    """
    azar = random.Random(semilla)
    carpeta.mkdir(parents=True, exist_ok=True)

    productos = []
    for i, (nombre, categoria, costo, precio, _) in enumerate(CATALOGO, start=1):
        productos.append(
            {
                "id": i,
                "nombre": nombre,
                "categoria": categoria,
                "costo_unitario": costo,
                "precio_venta": precio,
                "stock_inicial": azar.randint(60, 140),
            }
        )

    vendedores = [
        {"id": i, "nombre": n, "sucursal": s, "fecha_alta": f.isoformat()}
        for i, (n, s, f) in enumerate(VENDEDORES, start=1)
    ]

    stock = {p["id"]: p["stock_inicial"] for p in productos}
    compras, ventas = [], []
    movimientos = [
        {
            "id": p["id"],
            "fecha": (FECHA_INICIO - timedelta(days=1)).isoformat(),
            "producto_id": p["id"],
            "tipo": "stock_inicial",
            "cantidad": p["stock_inicial"],
            "referencia_id": "",
        }
        for p in productos
    ]

    for dia in range(DIAS):
        fecha = FECHA_INICIO + timedelta(days=dia)
        factor = FACTOR_DIA_SEMANA[fecha.weekday()]

        # 1) Reposición: lunes y jueves se compra lo que está por debajo del umbral.
        if fecha.weekday() in DIAS_DE_REPOSICION:
            for p, (*_, demanda) in zip(productos, CATALOGO, strict=True):
                umbral = demanda * 7
                if stock[p["id"]] < umbral and azar.random() < 0.85:
                    cantidad = demanda * azar.randint(8, 12)
                    costo = round(p["costo_unitario"] * azar.uniform(0.95, 1.06))
                    compras.append(
                        {
                            "id": len(compras) + 1,
                            "fecha": fecha.isoformat(),
                            "producto_id": p["id"],
                            "cantidad": cantidad,
                            "costo_unitario": costo,
                            "proveedor": PROVEEDORES[p["categoria"]],
                        }
                    )
                    stock[p["id"]] += cantidad
                    movimientos.append(
                        {
                            "id": len(movimientos) + 1,
                            "fecha": fecha.isoformat(),
                            "producto_id": p["id"],
                            "tipo": "entrada",
                            "cantidad": cantidad,
                            "referencia_id": f"C{len(compras)}",
                        }
                    )

        # 2) Ventas del día: la demanda varía por producto, día de la semana y azar.
        for p, (*_, demanda) in zip(productos, CATALOGO, strict=True):
            unidades_dia = round(demanda * factor * azar.uniform(0.5, 1.5))
            while unidades_dia > 0 and stock[p["id"]] > 0:
                cantidad = min(azar.choice([1, 1, 1, 2, 2, 3]), unidades_dia, stock[p["id"]])
                descuento = azar.choices([0.0, 0.05, 0.10], weights=[80, 15, 5])[0]
                ventas.append(
                    {
                        "id": len(ventas) + 1,
                        "fecha": fecha.isoformat(),
                        "producto_id": p["id"],
                        "cantidad": cantidad,
                        "precio_unitario": p["precio_venta"],
                        "descuento": descuento,
                        "vendedor_id": azar.choices(range(1, 6), weights=[30, 22, 20, 16, 12])[0],
                    }
                )
                stock[p["id"]] -= cantidad
                unidades_dia -= cantidad
                movimientos.append(
                    {
                        "id": len(movimientos) + 1,
                        "fecha": fecha.isoformat(),
                        "producto_id": p["id"],
                        "tipo": "salida",
                        "cantidad": cantidad,
                        "referencia_id": f"V{len(ventas)}",
                    }
                )

    tablas = {
        "productos": productos,
        "vendedores": vendedores,
        "compras": compras,
        "ventas": ventas,
        "movimientos_stock": movimientos,
    }
    for nombre, filas in tablas.items():
        _escribir_csv(carpeta / f"{nombre}.csv", filas)
    return {nombre: len(filas) for nombre, filas in tablas.items()}


def main() -> None:
    for tabla, cantidad in generar().items():
        print(f"{tabla}: {cantidad} registros")


if __name__ == "__main__":
    main()
