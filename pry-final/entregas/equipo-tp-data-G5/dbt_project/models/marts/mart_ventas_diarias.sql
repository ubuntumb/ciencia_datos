-- Resumen de ventas por día.
select
    fecha,
    case isodow(fecha)
        when 1 then 'lunes' when 2 then 'martes' when 3 then 'miércoles'
        when 4 then 'jueves' when 5 then 'viernes' when 6 then 'sábado'
        else 'domingo'
    end as dia_semana,
    count(*) as transacciones,
    sum(cantidad) as unidades_vendidas,
    sum(importe_bruto) as facturacion_bruta,
    sum(monto_descuento) as descuentos,
    sum(importe_neto) as facturacion_neta,
    round(sum(importe_neto) / count(*), 2) as ticket_promedio
from {{ ref('stg_ventas') }}
group by fecha
