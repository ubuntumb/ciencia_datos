select
    cast(id as bigint) as id,
    cast(fecha as date) as fecha,
    cast(producto_id as bigint) as producto_id,
    trim(tipo) as tipo,
    cast(cantidad as bigint) as cantidad,
    cast(referencia_id as bigint) as referencia_id
from {{ source('raw', 'movimientos_stock') }}
