-- Falla si algún producto queda con stock negativo en algún día.
select producto_id, fecha, stock_final_dia
from {{ ref('int_movimientos_stock') }}
where stock_final_dia < 0
