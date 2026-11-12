select
    cast(id as bigint) as id,
    cast(fecha as date) as fecha,
    cast(producto_id as bigint) as producto_id,
    cast(cantidad as bigint) as cantidad,
    cast(precio_unitario as decimal(18,2)) as precio_unitario,
    cast(descuento as decimal(5,4)) as descuento,
    cast(vendedor_id as bigint) as vendedor_id
from {{ source('raw', 'ventas') }}
