select
    cast(id as bigint) as id,
    trim(nombre) as nombre,
    trim(categoria) as categoria,
    cast(costo_unitario as decimal(18,2)) as costo_unitario,
    cast(precio_venta as decimal(18,2)) as precio_venta,
    cast(stock_inicial as bigint) as stock_inicial
from {{ source('raw', 'productos') }}
