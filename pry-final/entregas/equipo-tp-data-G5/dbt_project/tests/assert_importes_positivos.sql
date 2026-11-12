-- Falla si hay ventas o compras con cantidades o importes que no sean positivos.
select 'venta' as origen, venta_id as id
from {{ ref('stg_ventas') }}
where cantidad <= 0 or importe_neto <= 0
union all
select 'compra', compra_id
from {{ ref('stg_compras') }}
where cantidad <= 0 or costo_total <= 0
