with movimientos as (
    select m.*,
        case when m.tipo = 'entrada' then m.cantidad
             when m.tipo = 'salida' then -m.cantidad end as variacion,
        coalesce(c.producto_id, v.producto_id) as producto_documento,
        coalesce(c.fecha, v.fecha) as fecha_documento,
        coalesce(c.cantidad, v.cantidad) as cantidad_documento
    from {{ ref('stg_movimientos_stock') }} m
    left join {{ ref('stg_compras') }} c on m.tipo = 'entrada' and m.referencia_id = c.id
    left join {{ ref('stg_ventas') }} v on m.tipo = 'salida' and m.referencia_id = v.id
)
select m.*,
    p.stock_inicial + sum(m.variacion) over (
        partition by m.producto_id order by m.fecha, m.id rows unbounded preceding
    ) as saldo_stock
from movimientos m
join {{ ref('stg_productos') }} p on m.producto_id = p.id
