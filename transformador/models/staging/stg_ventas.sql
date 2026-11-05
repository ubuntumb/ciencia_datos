WITH raw_ventas as (
    SELECT * FROM {{ source('raw_data', 'raw_ventas') }}
)

SELECT 
    venta_id::INT AS venta_id,
    fecha_venta::TIMESTAMP AS fecha_venta,
    CAST(fecha_venta AS DATE) AS fecha_dia,
    producto_id::INT AS producto_id,
    vendedor_id::INT AS vendedor_id,
    cantidad::INT AS cantidad_vendida,
    precio_unitario::DECIMAL(12,2) AS precio_unitario,
    descuento::DECIMAL(12,2) AS descuento,
    ROUND((cantidad * precio_unitario - descuento), 2)::DECIMAL(12,2) AS venta_neta
FROM raw_ventas