WITH movimientos AS (
    SELECT * FROM {{ ref('stg_movimientos_stock') }}
),
productos AS (dagster dev -f orchestration/definitions.py

    SELECT * FROM {{ ref('stg_productos') }}
)
SELECT
    m.movimiento_id,
    m.fecha_movimiento::DATE AS fecha_movimiento,
    m.producto_id,
    p.nombre_producto,
    p.categoria,
    m.tipo_movimiento,
    m.cantidad AS variacion_stock
FROM movimientos m
JOIN productos p ON m.producto_id = p.producto_id