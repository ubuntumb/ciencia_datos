-- Movimientos de almacén: las salidas restan stock, el resto suma.
select
    cast(id as integer) as movimiento_id,
    cast(fecha as date) as fecha,
    cast(producto_id as integer) as producto_id,
    trim(tipo) as tipo,
    cast(cantidad as integer) as cantidad,
    case when trim(tipo) = 'salida' then -cast(cantidad as integer)
        else cast(cantidad as integer) end as cantidad_con_signo,
    nullif(trim(referencia_id), '') as referencia_id
from {{ source('raw', 'movimientos_stock') }}
