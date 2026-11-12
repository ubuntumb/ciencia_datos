select
    cast(id as bigint) as id,
    trim(nombre) as nombre,
    trim(sucursal) as sucursal,
    cast(fecha_alta as date) as fecha_alta
from {{ source('raw', 'vendedores') }}
