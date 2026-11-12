-- Inventario: rotación de cada producto y los que están por debajo del punto de reposición.
select
    nombre,
    stock_actual,
    punto_reposicion,
    dias_de_stock,
    rotacion,
    bajo_punto_reposicion
from marts.mart_rotacion_inventario
order by bajo_punto_reposicion desc, dias_de_stock
