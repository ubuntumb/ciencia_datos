# Pipeline analítico de un minimercado

Proyecto final del equipo `tp-data-Grupo-Johanna-Adalberto` para el módulo de Programación en Entornos de Datos. El flujo simula un minimercado y genera indicadores de ventas, rentabilidad e inventario a partir de datos sintéticos.

## Reproducir desde cero

Se necesita Python 3.12 y [uv](https://docs.astral.sh/uv/). Abrir la terminal en esta carpeta, donde están `pyproject.toml` y `uv.lock`. Estos comandos son para una terminal Bash o Zsh, como la del Codespace:

```bash
uv sync --locked
mkdir -p .dagster
cp orchestration/dagster.yaml .dagster/dagster.yaml
export DAGSTER_HOME="$PWD/.dagster"
export DAGSTER_DISABLE_TELEMETRY=1
uv run --locked dagster job execute -f orchestration/definitions.py -j minimercado
uv run --locked python -m pytest -q
uv run --locked ruff check .
uv run --locked ruff format --check .
```

La instalación necesita acceso a los paquetes. El flujo y las pruebas se ejecutan con archivos locales, sin API ni credenciales. El código desactiva la telemetría de dlt y de dbt; la configuración anterior hace lo mismo para Dagster.

### Ejecutar las etapas por separado

```bash
uv run --locked python generar_datos.py
uv run --locked python pipeline.py
uv run --locked python analisis.py
```

- `data/`: cinco CSV reproducibles con la semilla 42 y 90 días a partir del 1 de enero de 2026.
- `data.duckdb`: tablas de origen en `raw` y modelos en `analytics`. Cada ingesta reemplaza el contenido de las tablas de origen, de modo que volver a cargar los mismos CSV no duplica filas.
- `resultados.json`: estadística diaria, clasificación ABC, inventario, rentabilidad, vendedores y conciliaciones.
- `target/run_results.json`: resultado de los 13 modelos y 50 controles ejecutados por dbt.
- `informe.md`: arquitectura, decisiones, hallazgos, limitaciones y registro de aportes.

La prueba de integración ejecuta los cuatro activos de Dagster en una carpeta temporal y compara la facturación del resultado con el cálculo independiente a partir del CSV de ventas.

## Archivos del proyecto

Conservar en Git los CSV, el código, la configuración, las pruebas y el informe. La base DuckDB y los archivos de ejecución se regeneran con los comandos anteriores.
