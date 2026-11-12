select
    cast(id as integer) as venta_id,
    cast(fecha as date) as fecha_venta,
    cast(producto_id as integer) as producto_id,
    cast(cantidad as integer) as cantidad,
    cast(precio_unitario as double) as precio_unitario,
    cast(descuento as double) as descuento,
    cast(vendedor_id as integer) as vendedor_id
from {{ source('main', 'ventas') }}