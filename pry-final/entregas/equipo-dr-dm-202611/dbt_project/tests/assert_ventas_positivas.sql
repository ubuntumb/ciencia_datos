-- Retorna registros si la facturación resulta negativa, lo cual invalidaría el test
select *
from {{ ref('mart_ventas_diarias') }}
where facturacion_total < 0