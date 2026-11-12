with compras as (
    select producto_id, sum(cantidad) as unidades, sum(cantidad * costo_unitario) as costo_total
    from {{ ref('stg_compras') }}
    group by producto_id
)
select p.id as producto_id,
    cast((p.stock_inicial * p.costo_unitario + coalesce(c.costo_total, 0))
        / nullif(p.stock_inicial + coalesce(c.unidades, 0), 0)
        as decimal(18, 6)) as costo_promedio
from {{ ref('stg_productos') }} p
left join compras c on c.producto_id = p.id
