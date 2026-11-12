select fecha, count(*) as registros_venta, sum(cantidad) as unidades,
    sum(facturacion) as facturacion
from {{ ref('int_ventas_valorizadas') }}
group by fecha
