select
    cast(id as integer) as producto_id,
    cast(nombre as varchar) as nombre_producto,
    cast(categoria as varchar) as categoria,
    cast(costo_unitario as double) as costo_unitario,
    cast(precio_venta as double) as precio_venta,
    cast(stock_inicial as integer) as stock_inicial
from {{ source('main', 'productos') }}