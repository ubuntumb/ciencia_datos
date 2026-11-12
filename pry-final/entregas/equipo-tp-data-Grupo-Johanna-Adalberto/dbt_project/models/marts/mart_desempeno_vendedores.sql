select p.id as vendedor_id, p.nombre, p.sucursal,
    count(v.id) as registros_venta, coalesce(sum(v.cantidad), 0) as unidades,
    coalesce(sum(v.facturacion), 0) as facturacion
from {{ ref('stg_vendedores') }} p
left join {{ ref('int_ventas_valorizadas') }} v on v.vendedor_id = p.id
group by p.id, p.nombre, p.sucursal
