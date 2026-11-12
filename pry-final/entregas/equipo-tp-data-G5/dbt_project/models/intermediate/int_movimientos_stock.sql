-- Stock de cada producto al cierre de cada día, calculado desde compras y ventas.
with calendario as (
    select distinct fecha from {{ ref('stg_ventas') }}
    union
    select distinct fecha from {{ ref('stg_compras') }}
),

entradas as (
    select producto_id, fecha, sum(cantidad) as entradas
    from {{ ref('stg_compras') }}
    group by producto_id, fecha
),

salidas as (
    select producto_id, fecha, sum(cantidad) as salidas
    from {{ ref('stg_ventas') }}
    group by producto_id, fecha
),

diario as (
    select
        p.producto_id,
        c.fecha,
        p.stock_inicial,
        coalesce(e.entradas, 0) as entradas,
        coalesce(s.salidas, 0) as salidas
    from {{ ref('stg_productos') }} as p
    cross join calendario as c
    left join entradas as e on e.producto_id = p.producto_id and e.fecha = c.fecha
    left join salidas as s on s.producto_id = p.producto_id and s.fecha = c.fecha
)

select
    producto_id,
    fecha,
    entradas,
    salidas,
    stock_inicial + sum(entradas - salidas) over (
        partition by producto_id order by fecha
        rows between unbounded preceding and current row
    ) as stock_final_dia
from diario
