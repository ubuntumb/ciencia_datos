select
    v.vendedor_id,
    v.nombre_vendedor,
    v.sucursal,
    count(vt.venta_id) as total_ventas_realizadas,
    sum(vt.cantidad) as unidades_vendidas,
    sum(vt.cantidad * vt.precio_unitario * (1 - vt.descuento)) as venta_acumulada_total
from {{ ref('stg_vendedores') }} v
left join {{ ref('stg_ventas') }} vt on v.vendedor_id = vt.vendedor_id
group by 1, 2, 3