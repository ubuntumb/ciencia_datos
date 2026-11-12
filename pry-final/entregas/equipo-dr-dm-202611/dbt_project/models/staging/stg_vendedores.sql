select
    cast(id as integer) as vendedor_id,
    cast(nombre as varchar) as nombre_vendedor,
    cast(sucursal as varchar) as sucursal,
    cast(fecha_alta as date) as fecha_alta
from {{ source('main', 'vendedores') }}