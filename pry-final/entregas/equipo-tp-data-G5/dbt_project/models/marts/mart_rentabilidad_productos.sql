-- Ganancia bruta por producto: ingresos netos menos el costo de lo vendido.
-- El costo unitario es el promedio ponderado del stock inicial y de todas las compras.
with ventas as (
    select producto_id, sum(cantidad) as unidades, sum(importe_neto) as ingresos
    from {{ ref('stg_ventas') }}
    group by producto_id
),

compras as (
    select producto_id, sum(cantidad) as unidades, sum(costo_total) as costo
    from {{ ref('stg_compras') }}
    group by producto_id
),

costos as (
    select
        p.producto_id,
        (p.stock_inicial * p.costo_unitario + coalesce(c.costo, 0))
        / (p.stock_inicial + coalesce(c.unidades, 0)) as costo_promedio
    from {{ ref('stg_productos') }} as p
    left join compras as c on c.producto_id = p.producto_id
)

select
    p.producto_id,
    p.nombre,
    p.categoria,
    coalesce(v.unidades, 0) as unidades_vendidas,
    coalesce(v.ingresos, 0) as ingresos_netos,
    round(k.costo_promedio, 2) as costo_unitario_promedio,
    round(coalesce(v.unidades, 0) * k.costo_promedio, 2) as costo_de_ventas,
    round(coalesce(v.ingresos, 0) - coalesce(v.unidades, 0) * k.costo_promedio, 2)
        as ganancia_bruta,
    round(
        100 * (coalesce(v.ingresos, 0) - coalesce(v.unidades, 0) * k.costo_promedio)
        / nullif(v.ingresos, 0),
        2
    ) as margen_bruto_pct
from {{ ref('stg_productos') }} as p
left join ventas as v on v.producto_id = p.producto_id
left join costos as k on k.producto_id = p.producto_id
