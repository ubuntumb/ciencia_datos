with errores as (
    select id from {{ ref('int_movimientos_stock') }}
    where saldo_stock < 0
       or tipo not in ('entrada', 'salida')
       or cantidad <= 0
       or producto_id is distinct from producto_documento
       or fecha is distinct from fecha_documento
       or cantidad is distinct from cantidad_documento
), duplicados as (
    select min(id) as id
    from {{ ref('int_movimientos_stock') }}
    group by tipo, referencia_id having count(*) <> 1
), faltantes as (
    select c.id from {{ ref('stg_compras') }} c
    where not exists (
        select 1 from {{ ref('int_movimientos_stock') }} m
        where m.tipo = 'entrada' and m.referencia_id = c.id
    )
    union all
    select v.id from {{ ref('stg_ventas') }} v
    where not exists (
        select 1 from {{ ref('int_movimientos_stock') }} m
        where m.tipo = 'salida' and m.referencia_id = v.id
    )
)
select * from errores union all select * from duplicados union all select * from faltantes
