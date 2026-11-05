WITH raw_vendedores AS (
    SELECT * FROM {{ source('raw_data', 'raw_vendedores') }}
)
SELECT
    vendedor_id::INT AS vendedor_id,
    TRIM(nombre_vendedor) AS nombre_vendedor,
    TRIM(sucursal) AS sucursal,
    fecha_alta::DATE AS fecha_alta
FROM raw_vendedores