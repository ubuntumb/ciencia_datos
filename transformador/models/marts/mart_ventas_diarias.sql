WITH ventas AS (
    SELECT * FROM {{ ref('stg_ventas') }}
)
SELECT
    fecha_dia AS fecha,
    COUNT(venta_id) AS total_transacciones,
    SUM(cantidad_vendida) AS total_unidades,
    ROUND(SUM(venta_neta), 2)::DECIMAL(12,2) AS facturacion_total,
    ROUND(AVG(venta_neta), 2)::DECIMAL(12,2) AS ticket_promedio_diario
FROM ventas
GROUP BY fecha_dia