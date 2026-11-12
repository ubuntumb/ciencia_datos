-- Ventas: tipos numéricos e importes bruto, descuento y neto de cada línea.
with tipado as (
    select
        cast(id as integer) as venta_id,
        cast(fecha as date) as fecha,
        cast(producto_id as integer) as producto_id,
        cast(vendedor_id as integer) as vendedor_id,
        cast(cantidad as integer) as cantidad,
        cast(precio_unitario as decimal(14, 2)) as precio_unitario,
        cast(descuento as decimal(5, 2)) as descuento
    from {{ source('raw', 'ventas') }}
)

select
    *,
    cantidad * precio_unitario as importe_bruto,
    round(cantidad * precio_unitario * descuento, 2) as monto_descuento,
    round(cantidad * precio_unitario * (1 - descuento), 2) as importe_neto
from tipado
