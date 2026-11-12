select id from {{ ref('stg_ventas') }}
where cantidad <= 0 or precio_unitario <= 0 or descuento < 0 or descuento >= 1
union all
select id from {{ ref('stg_compras') }}
where cantidad <= 0 or costo_unitario <= 0
union all
select id from {{ ref('stg_productos') }}
where stock_inicial < 0 or costo_unitario <= 0 or precio_venta <= 0
