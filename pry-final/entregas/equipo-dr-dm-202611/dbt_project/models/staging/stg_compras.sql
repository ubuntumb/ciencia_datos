select
    cast(id as integer) as compra_id,
    cast(fecha as date) as fecha_compra,
    cast(producto_id as integer) as producto_id,
    cast(cantidad as integer) as cantidad,
    cast(costo_unitario as double) as costo_unitario,
    cast(proveedor as varchar) as proveedor
from {{ source('main', 'compras') }}