-- Rotación, días de stock disponibles y punto de reposición por producto.
with resumen as (
    select
        producto_id,
        count(*) as dias_observados,
        sum(salidas) as unidades_vendidas,
        avg(stock_final_dia) as stock_promedio,
        arg_max(stock_final_dia, fecha) as stock_actual
    from {{ ref('int_movimientos_stock') }}
    group by producto_id
),

calculos as (
    select
        *,
        unidades_vendidas / dias_observados as demanda_diaria,
        ceil(unidades_vendidas / dias_observados * {{ var('dias_cobertura') }})
            as punto_reposicion
    from resumen
)

select
    c.producto_id,
    p.nombre,
    p.categoria,
    c.stock_actual,
    round(c.stock_promedio, 2) as stock_promedio,
    c.unidades_vendidas,
    round(c.demanda_diaria, 2) as demanda_diaria,
    round(c.unidades_vendidas / nullif(c.stock_promedio, 0), 2) as rotacion,
    round(c.stock_actual / nullif(c.demanda_diaria, 0), 1) as dias_de_stock,
    cast(c.punto_reposicion as integer) as punto_reposicion,
    c.stock_actual < c.punto_reposicion as bajo_punto_reposicion
from calculos as c
inner join {{ ref('stg_productos') }} as p on p.producto_id = c.producto_id
