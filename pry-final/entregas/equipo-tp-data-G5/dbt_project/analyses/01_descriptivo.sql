-- Análisis descriptivo: facturación total, unidades y estadísticas de la venta diaria.
select
    sum(facturacion_neta) as facturacion_total,
    sum(unidades_vendidas) as unidades_vendidas,
    count(*) as dias,
    round(avg(facturacion_neta), 0) as promedio_diario,
    round(median(facturacion_neta), 0) as mediana_diaria,
    round(stddev_samp(facturacion_neta), 0) as desviacion_estandar_diaria,
    min(facturacion_neta) as dia_minimo,
    max(facturacion_neta) as dia_maximo
from marts.mart_ventas_diarias
