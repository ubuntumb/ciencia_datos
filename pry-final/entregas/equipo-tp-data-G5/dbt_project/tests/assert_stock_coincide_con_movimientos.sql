-- Falla si el stock calculado desde compras y ventas no coincide
-- con la suma de la tabla de movimientos de almacén.
with calculado as (
    select producto_id, arg_max(stock_final_dia, fecha) as stock
    from {{ ref('int_movimientos_stock') }}
    group by producto_id
),

movimientos as (
    select producto_id, sum(cantidad_con_signo) as stock
    from {{ ref('stg_movimientos_stock') }}
    group by producto_id
)

select c.producto_id, c.stock as stock_calculado, m.stock as stock_movimientos
from calculado as c
inner join movimientos as m on m.producto_id = c.producto_id
where c.stock <> m.stock
