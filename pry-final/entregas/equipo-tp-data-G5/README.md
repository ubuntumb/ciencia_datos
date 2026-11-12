# Pipeline analítico de un minimercado · equipo tp-data-G5

Pipeline reproducible de punta a punta: datos sintéticos de un minimercado (julio a septiembre
de 2026), ingesta con dlt a DuckDB, modelado con dbt, análisis en SQL y orquestación con Dagster.

| Integrante | Rol | Archivos |
| --- | --- | --- |
| mjgo139 | Ingeniería de Datos | `generar_datos.py`, `data/`, `pipeline.py` |
| fabioAlfonsoUNC | Analytics Engineering | `dbt_project/`, `consultas.py` |
| celso2000 | Orquestación y QA | `orchestration/`, `test_pipeline.py`, `informe.md` |

## Reproducir todo desde cero

Desde la raíz del repositorio, en el Codespace del curso (las dependencias ya están en `.venv`):

```bash
source .venv/bin/activate
cd pry-final/entregas/equipo-tp-data-G5
```

### Opción 1: paso a paso

```bash
python generar_datos.py          # 1. Escribe los CSV en data/ (semilla 42)
python pipeline.py               # 2. Carga data/ en data.duckdb, esquema raw (dlt, idempotente)
cd dbt_project
dbt build --profiles-dir .       # 3. Modelos staging, intermediate y marts + 41 pruebas de calidad
cd ..
python consultas.py              # 4. Consultas de análisis (dbt_project/analyses/)
pytest -v                        # 5. Pruebas automatizadas
```

### Opción 2: todo con Dagster

```bash
# Línea de comandos: ejecuta los 4 assets en orden
dagster job execute -f orchestration/definitions.py -j pipeline_completo

# Interfaz web (http://localhost:3000): Assets → Materialize all
dagster dev -f orchestration/definitions.py
```

## Qué hay en cada carpeta

| Ruta | Contenido |
| --- | --- |
| `generar_datos.py` | Genera productos, vendedores, compras, ventas y movimientos de stock (92 días) |
| `data/` | Los 5 CSV generados con la semilla 42 |
| `pipeline.py` | Fuente dlt con un recurso por CSV, `merge` por `id` hacia `data.duckdb` |
| `dbt_project/models/staging/` | Limpieza y tipos: `stg_productos`, `stg_vendedores`, `stg_compras`, `stg_ventas`, `stg_movimientos_stock` |
| `dbt_project/models/intermediate/` | `int_movimientos_stock`: stock de cada producto al cierre de cada día |
| `dbt_project/models/marts/` | Ventas diarias, rentabilidad, rotación de inventario, desempeño de vendedores y clasificación ABC |
| `dbt_project/tests/` | Pruebas SQL propias: stock nunca negativo, stock que cuadra con los movimientos, importes positivos y ABC que suma 100 % |
| `dbt_project/analyses/` | Consultas de negocio: descriptivo, inventario y comercial |
| `orchestration/definitions.py` | Assets de Dagster y el job `pipeline_completo` |
| `test_pipeline.py` | Reproducibilidad, esquema tras la ingesta, idempotencia y prueba de punta a punta |
| `informe.md` | Informe técnico |

`data.duckdb` y las carpetas que generan dbt y Dagster no se suben al repositorio (ver `.gitignore`).
