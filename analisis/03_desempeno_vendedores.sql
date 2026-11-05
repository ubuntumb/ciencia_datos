SELECT 
    vendedor_id,
    nombre_vendedor,
    sucursal,
    total_transacciones,
    ingresos_generados,
    ticket_promedio
FROM marts.mart_desempeno_vendedores
ORDER BY ingresos_generados DESC;
