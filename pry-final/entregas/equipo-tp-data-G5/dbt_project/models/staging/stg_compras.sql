-- Compras a proveedores: tipos numéricos y costo total de cada compra.
with tipado as (
    select
        cast(id as integer) as compra_id,
        cast(fecha as date) as fecha,
        cast(producto_id as integer) as producto_id,
        cast(cantidad as integer) as cantidad,
        cast(costo_unitario as decimal(14, 2)) as costo_unitario,
        trim(proveedor) as proveedor
    from {{ source('raw', 'compras') }}
)

select
    *,
    cantidad * costo_unitario as costo_total
from tipado
