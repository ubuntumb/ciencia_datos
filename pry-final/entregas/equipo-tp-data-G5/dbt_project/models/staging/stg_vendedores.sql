-- Vendedores con su sucursal y fecha de alta como fecha real.
select
    cast(id as integer) as vendedor_id,
    trim(nombre) as nombre,
    trim(sucursal) as sucursal,
    cast(fecha_alta as date) as fecha_alta
from {{ source('raw', 'vendedores') }}
