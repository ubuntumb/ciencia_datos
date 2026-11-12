with orden as (
    select producto_id, nombre, unidades, facturacion,
        sum(unidades) over () as total_unidades,
        sum(unidades) over (
            order by unidades desc, producto_id rows unbounded preceding
        ) as unidades_acumuladas
    from {{ ref('mart_rentabilidad_productos') }}
)
select producto_id, nombre, unidades, facturacion,
    unidades_acumuladas * 1.0 / nullif(total_unidades, 0) as proporcion_acumulada,
    case when unidades = 0 then 'C'
         when (unidades_acumuladas - unidades) < 0.80 * total_unidades then 'A'
         when (unidades_acumuladas - unidades) < 0.95 * total_unidades then 'B'
         else 'C' end as clase
from orden
