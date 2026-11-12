-- Ventas acumuladas por vendedor y su participación en el total.
with por_vendedor as (
    select
        vendedor_id,
        count(*) as transacciones,
        sum(cantidad) as unidades_vendidas,
        sum(importe_neto) as facturacion_neta
    from {{ ref('stg_ventas') }}
    group by vendedor_id
)

select
    v.vendedor_id,
    v.nombre,
    v.sucursal,
    pv.transacciones,
    pv.unidades_vendidas,
    pv.facturacion_neta,
    round(pv.facturacion_neta / pv.transacciones, 2) as ticket_promedio,
    round(100 * pv.facturacion_neta / sum(pv.facturacion_neta) over (), 2) as participacion_pct,
    rank() over (order by pv.facturacion_neta desc) as ranking
from {{ ref('stg_vendedores') }} as v
inner join por_vendedor as pv on pv.vendedor_id = v.vendedor_id
