SELECT 
    producto_id, 
    nombre_producto, 
    categoria,
    stock_actual, 
    dias_stock_disponibles,
    CASE 
        WHEN dias_stock_disponibles < 15 THEN 'REPOSICION URGENTE' 
        WHEN dias_stock_disponibles < 30 THEN 'ALERTA REPOSICION'
        ELSE 'STOCK OK' 
    END AS estado_stock
FROM marts.mart_rotacion_inventario
ORDER BY dias_stock_disponibles ASC