SELECT
    ROUND(SUM(facturacion_total), 2) AS facturacion_total,
    SUM(total_unidades) AS total_unidades_vendidas,
    ROUND(AVG(facturacion_total), 2) AS promedio_facturacion_diaria,
    ROUND(MEDIAN(facturacion_total), 2) AS mediana_facturacion_diaria,
    ROUND(STDDEV(facturacion_total), 2) AS desviacion_estandar_diaria
FROM marts.mart_ventas_diarias;