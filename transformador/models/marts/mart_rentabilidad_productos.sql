WITH productos AS (
    SELECT * FROM {{ ref('stg_productos') }}
),
ventas AS (
    SELECT * FROM {{ ref('stg_ventas') }}
)

SELECT
    p.producto_id,
    p.nombre_producto,
    p.categoria,
    COALESCE(SUM(v.cantidad_vendida), 0) AS unidades_vendidas,
    COALESCE(ROUND(SUM(v.venta_neta), 2), 0.00)::DECIMAL(12,2) AS ingresos_totales,
    COALESCE(ROUND(SUM(v.cantidad_vendida * p.costo_unitario), 2), 0.00)::DECIMAL(12,2) AS costo_total_ventas,
    COALESCE(ROUND(SUM(v.venta_neta) - SUM(v.cantidad_vendida * p.costo_unitario), 2), 0.00)::DECIMAL(12,2) AS ganancia_bruta,
    COALESCE(ROUND((SUM(v.venta_neta) - SUM(v.cantidad_vendida * p.costo_unitario)) / NULLIF(SUM(v.venta_neta), 0) * 100, 2), 0.00)::DECIMAL(5,2) AS margen_porcentaje
FROM productos p
LEFT JOIN ventas v ON p.producto_id = v.producto_id
GROUP BY p.producto_id, p.nombre_producto, p.categoria
