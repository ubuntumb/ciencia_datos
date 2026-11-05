WITH vendedores AS (
    SELECT * FROM {{ ref('stg_vendedores') }}
),
ventas AS (
    SELECT * FROM {{ ref('stg_ventas') }}
)
SELECT
    v.vendedor_id,
    v.nombre_vendedor,
    v.sucursal,
    COUNT(vt.venta_id) AS total_transacciones,
    COALESCE(SUM(vt.cantidad_vendida), 0) AS total_unidades_vendidas,
    COALESCE(ROUND(SUM(vt.venta_neta), 2), 0.00)::DECIMAL(12,2) AS ingresos_generados,
    COALESCE(ROUND(AVG(vt.venta_neta), 2), 0.00)::DECIMAL(12,2) AS ticket_promedio
FROM vendedores v
LEFT JOIN ventas vt ON v.vendedor_id = vt.vendedor_id
GROUP BY v.vendedor_id, v.nombre_vendedor, v.sucursal