WITH raw_movimientos AS (
    SELECT * FROM {{ source('raw_data', 'raw_movimientos_stock') }}
)
SELECT
    movimiento_id::INT AS movimiento_id,
    fecha_movimiento::DATE AS fecha_movimiento,
    producto_id::INT AS producto_id,
    TRIM(tipo_movimiento) AS tipo_movimiento,
    cantidad::INT AS cantidad
FROM raw_movimientos