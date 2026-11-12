select p.id as producto_id, p.nombre, p.categoria,
    coalesce(sum(v.cantidad), 0) as unidades,
    coalesce(sum(v.facturacion), 0) as facturacion,
    coalesce(sum(v.costo_ventas), 0) as costo_ventas,
    coalesce(sum(v.facturacion - v.costo_ventas), 0) as ganancia_bruta
from {{ ref('stg_productos') }} p
left join {{ ref('int_ventas_valorizadas') }} v on v.producto_id = p.id
group by p.id, p.nombre, p.categoria
