WITH productos AS (
    SELECT * FROM {{ ref('stg_productos') }}
),
movimientos AS (
    SELECT * FROM {{ ref('int_movimientos_stock') }}
),
balance_movimientos AS (
    SELECT
        producto_id,
        SUM(variacion_stock) AS neto_movimientos,
        ABS(SUM(CASE WHEN variacion_stock < 0 THEN variacion_stock ELSE 0 END)) AS total_ventas_unidades
    FROM movimientos
    GROUP BY producto_id
)
SELECT
    p.producto_id,
    p.nombre_producto,
    p.categoria,
    p.stock_inicial,
    COALESCE(b.neto_movimientos, 0) AS neto_movimientos,
    (p.stock_inicial + COALESCE(b.neto_movimientos, 0)) AS stock_actual,
    ROUND(COALESCE(b.total_ventas_unidades, 0) / 90.0, 2) AS promedio_ventas_diarias,
    ROUND((p.stock_inicial + COALESCE(b.neto_movimientos, 0)) / NULLIF(COALESCE(b.total_ventas_unidades, 0) / 90.0, 0), 1) AS dias_stock_disponibles
FROM productos p
LEFT JOIN balance_movimientos b ON p.producto_id = b.producto_id