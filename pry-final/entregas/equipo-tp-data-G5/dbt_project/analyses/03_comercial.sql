-- Comercial: ranking de vendedores y distribución ABC de la facturación.
select
    'vendedor' as tipo,
    nombre as detalle,
    facturacion_neta,
    participacion_pct
from marts.mart_desempeno_vendedores

union all

select
    'clase ' || clase_abc,
    count(*) || ' productos',
    sum(facturacion_neta),
    round(sum(participacion_pct), 2)
from marts.mart_clasificacion_abc
group by clase_abc

order by tipo, facturacion_neta desc
