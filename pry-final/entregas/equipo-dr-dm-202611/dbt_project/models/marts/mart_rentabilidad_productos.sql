with ventas as (
    select * from {{ ref('stg_ventas') }}
),
productos as (
    select * from {{ ref('stg_productos') }}
),
metricas as (
    select
        p.producto_id,
        p.nombre_producto,
        p.categoria,
        coalesce(sum(v.cantidad), 0) as total_unidades_vendidas,
        coalesce(sum(v.cantidad * v.precio_unitario * (1 - v.descuento)), 0) as ingresos_totales,
        coalesce(sum(v.cantidad * p.costo_unitario), 0) as costo_total,
        coalesce(sum(v.cantidad * v.precio_unitario * (1 - v.descuento)), 0) - coalesce(sum(v.cantidad * p.costo_unitario), 0) as ganancia_bruta
    from productos p
    left join ventas v on p.producto_id = v.producto_id
    group by 1, 2, 3
),
abc_acumulado as (
    select
        *,
        sum(ingresos_totales) over (order by ingresos_totales desc) / nullif(sum(ingresos_totales) over (), 0) as pct_acumulado
    from metricas
)
select
    producto_id,
    nombre_producto,
    categoria,
    total_unidades_vendidas,
    ingresos_totales,
    costo_total,
    ganancia_bruta,
    case
        when pct_acumulado <= 0.70 then 'A'
        when pct_acumulado <= 0.90 then 'B'
        else 'C'
    end as clasificacion_abc
from abc_acumulado