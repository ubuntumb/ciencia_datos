-- Clasificación ABC por facturación: A reúne el primer 80 %, B hasta el 95 %, C el resto.
with por_producto as (
    select
        p.producto_id,
        p.nombre,
        p.categoria,
        coalesce(sum(v.importe_neto), 0) as facturacion_neta
    from {{ ref('stg_productos') }} as p
    left join {{ ref('stg_ventas') }} as v on v.producto_id = p.producto_id
    group by p.producto_id, p.nombre, p.categoria
),

acumulado as (
    select
        *,
        100 * facturacion_neta / sum(facturacion_neta) over () as participacion_pct,
        100 * sum(facturacion_neta) over (
            order by facturacion_neta desc, producto_id
            rows between unbounded preceding and current row
        ) / sum(facturacion_neta) over () as acumulado_pct
    from por_producto
)

select
    producto_id,
    nombre,
    categoria,
    facturacion_neta,
    round(participacion_pct, 2) as participacion_pct,
    round(acumulado_pct, 2) as acumulado_pct,
    case
        when acumulado_pct - participacion_pct < 80 then 'A'
        when acumulado_pct - participacion_pct < 95 then 'B'
        else 'C'
    end as clase_abc
from acumulado
