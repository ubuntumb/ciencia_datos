with stock_inicial as (
    select producto_id, stock_inicial from {{ ref('stg_productos') }}
),
movimientos as (
    select
        producto_id,
        sum(cambio_neto_stock) as cambio_total
    from {{ ref('int_movimientos_stock') }}
    group by 1
),
ventas as (
    select
        producto_id,
        sum(cantidad) / 90.0 as venta_diaria_promedio
    from {{ ref('stg_ventas') }}
    group by 1
)
select
    s.producto_id,
    s.stock_inicial + coalesce(m.cambio_total, 0) as stock_actual,
    v.venta_diaria_promedio,
    case
        when coalesce(v.venta_diaria_promedio, 0) = 0 then 999
        else round((s.stock_inicial + coalesce(m.cambio_total, 0)) / v.venta_diaria_promedio, 1)
    end as dias_stock_disponibles
from stock_inicial s
left join movimientos m on s.producto_id = m.producto_id
left join ventas v on s.producto_id = v.producto_id