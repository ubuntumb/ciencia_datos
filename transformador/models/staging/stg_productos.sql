WITH raw_productos AS (
    SELECT * FROM {{ source('raw_data', 'raw_productos') }}
)
SELECT
    producto_id::INT AS producto_id,
    TRIM(nombre_producto) AS nombre_producto,
    TRIM(categoria) AS categoria,
    costo_unitario::DECIMAL(12,2) AS costo_unitario,
    precio_venta::DECIMAL(12,2) AS precio_venta,
    stock_inicial::INT AS stock_inicial
FROM raw_productos