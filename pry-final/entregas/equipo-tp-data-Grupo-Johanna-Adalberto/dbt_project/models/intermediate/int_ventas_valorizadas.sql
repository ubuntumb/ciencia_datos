select v.*,
    cast(round(v.cantidad * v.precio_unitario * (1 - v.descuento), 2)
        as decimal(18, 2)) as facturacion,
    cast(round(v.cantidad * c.costo_promedio, 2) as decimal(18, 2)) as costo_ventas
from {{ ref('stg_ventas') }} v
join {{ ref('int_costo_productos') }} c on c.producto_id = v.producto_id
