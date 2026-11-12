select
    cast(id as integer) as movimiento_id,
    cast(fecha as date) as fecha,
    cast(producto_id as integer) as producto_id,
    cast(tipo_movimiento as varchar) as tipo_movimiento,
    cast(cantidad as integer) as cantidad,
    case
        when tipo_movimiento = 'ENTRADA' then cantidad
        when tipo_movimiento = 'SALIDA' then -cantidad
        else 0
    end as cambio_neto_stock
from {{ source('main', 'movimientos_stock') }}