WITH rentabilidad AS (
    SELECT * FROM {{ ref('mart_rentabilidad_productos') }}
),
ventas_acumuladas AS (
    SELECT
        producto_id,
        nombre_producto,
        ingresos_totales,
        SUM(ingresos_totales) OVER () AS ingresos_globales,
        SUM(ingresos_totales) OVER (ORDER BY ingresos_totales DESC ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS ingresos_acumulados
    FROM rentabilidad
)
SELECT
    producto_id,
    nombre_producto,
    ingresos_totales,
    ROUND((ingresos_acumulados / ingresos_globales) * 100, 2) AS pct_acumulado,
    CASE
        WHEN (ingresos_acumulados / ingresos_globales) <= 0.70 THEN 'A (Alto Valor)'
        WHEN (ingresos_acumulados / ingresos_globales) <= 0.90 THEN 'B (Valor Medio)'
        ELSE 'C (Bajo Valor)'
    END AS clasificacion_abc
FROM ventas_acumuladas