SELECT 
    'raw_ventas' AS tabla, 
    COUNT(*) AS total_registros 
FROM raw_data.raw_ventas
UNION ALL
SELECT 
    'raw_compras' AS tabla, 
    COUNT(*) AS total_registros 
FROM raw_data.raw_compras
UNION ALL
SELECT 
    'mart_ventas_diarias' AS tabla, 
    COUNT(*) AS total_registros 
FROM marts.mart_ventas_diarias
UNION ALL
SELECT 
    'mart_clasificacion_abc_productos' AS tabla, 
    COUNT(*) AS total_registros 
FROM marts.mart_clasificacion_abc_productos;