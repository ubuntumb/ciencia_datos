WITH raw_compras AS (
    SELECT * FROM {{ source('raw_data', 'raw_compras') }}
)
SELECT
    compra_id::INT AS compra_id,
    fecha_compra::DATE AS fecha_compra,
    producto_id::INT AS producto_id,
    cantidad::INT AS cantidad_comprada,
    costo_unitario::DECIMAL(12,2) AS costo_unitario,
    TRIM(proveedor) AS proveedor,
    ROUND((cantidad * costo_unitario), 2)::DECIMAL(12,2) AS costo_total_compra
FROM raw_compras