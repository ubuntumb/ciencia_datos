select
    fecha_venta as fecha,
    count(venta_id) as total_transacciones,
    sum(cantidad) as total_unidades_vendidas,
    sum(cantidad * precio_unitario * (1 - descuento)) as facturacion_total,
    avg(cantidad * precio_unitario * (1 - descuento)) as ticket_promedio,
    stddev(cantidad * precio_unitario * (1 - descuento)) as desviacion_std_ventas
from {{ ref('stg_ventas') }}
group by 1