SELECT 
    clasificacion_abc,
    COUNT(producto_id) AS cantidad_productos,
    ROUND(SUM(ingresos_totales), 2) AS ingresos_grupo
FROM marts.mart_clasificacion_abc_productos
GROUP BY clasificacion_abc
ORDER BY clasificacion_abc ASC;