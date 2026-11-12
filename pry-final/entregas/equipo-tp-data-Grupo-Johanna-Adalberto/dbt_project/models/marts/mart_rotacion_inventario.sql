with calendario as (
    select cast(dia as date) as fecha
    from generate_series(
        (select min(fecha) from {{ ref('stg_ventas') }}),
        (select max(fecha) from {{ ref('stg_ventas') }}),
        interval 1 day
    ) as dias(dia)
), diarios as (
    select producto_id, fecha, sum(variacion) as cambio
    from {{ ref('int_movimientos_stock') }}
    group by producto_id, fecha
), saldos as (
    select p.id as producto_id, p.nombre, c.fecha,
        p.stock_inicial + sum(coalesce(d.cambio, 0)) over (
            partition by p.id order by c.fecha rows unbounded preceding
        ) as stock_cierre
    from {{ ref('stg_productos') }} p
    cross join calendario c
    left join diarios d on d.producto_id = p.id and d.fecha = c.fecha
), resumen as (
    select producto_id, nombre, arg_max(stock_cierre, fecha) as stock_final,
        avg(stock_cierre) as stock_promedio, count(*) as dias_periodo
    from saldos
    group by producto_id, nombre
), metricas as (
    select r.*,
        v.unidades * 1.0 / r.dias_periodo as demanda_diaria,
        v.costo_ventas / nullif(r.stock_promedio * c.costo_promedio, 0) as rotacion,
        r.stock_final / nullif(v.unidades * 1.0 / r.dias_periodo, 0) as dias_disponibles,
        cast(ceil(9.0 * v.unidades / r.dias_periodo) as integer) as punto_reposicion
    from resumen r
    join {{ ref('mart_rentabilidad_productos') }} v using (producto_id)
    join {{ ref('int_costo_productos') }} c using (producto_id)
)
select *, stock_final < punto_reposicion as reponer
from metricas
