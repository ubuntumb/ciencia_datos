#!/bin/bash

# Define el nombre de la carpeta de la entrega
NOMBRE_EQUIPO="dr-dm-202611"
BASE_DIR="./"

echo "Creando estructura completa de directorios y archivos vacíos en: ${BASE_DIR}"

# -----------------------------------------------------------------------------
# 1. Creación de Directorios
# -----------------------------------------------------------------------------
mkdir -p "${BASE_DIR}/data"
mkdir -p "${BASE_DIR}/dbt_project/models/staging"
mkdir -p "${BASE_DIR}/dbt_project/models/intermediate"
mkdir -p "${BASE_DIR}/dbt_project/models/marts"
mkdir -p "${BASE_DIR}/dbt_project/tests"
mkdir -p "${BASE_DIR}/orchestration"

# -----------------------------------------------------------------------------
# 2. Archivos de la Raíz del Proyecto
# -----------------------------------------------------------------------------
touch "${BASE_DIR}/pyproject.toml"
touch "${BASE_DIR}/README.md"
touch "${BASE_DIR}/generar_datos.py"
touch "${BASE_DIR}/pipeline.py"
touch "${BASE_DIR}/test_pipeline.py"
touch "${BASE_DIR}/informe.md"

cat << 'EOF' > "${BASE_DIR}/.gitignore"
__pycache__/
*.pyc
.pytest_cache/
.dagster/
dbt_project/target/
dbt_project/dbt_packages/
data.duckdb
data/*.csv
EOF

# -----------------------------------------------------------------------------
# 3. Proyecto dbt - Archivos de Configuración Base
# -----------------------------------------------------------------------------
cat << 'EOF' > "${BASE_DIR}/dbt_project/dbt_project.yml"
name: 'minimercado_dbt'
version: '1.0.0'
config-version: 2

profile: 'minimercado'

model-paths: ["models"]
test-paths: ["tests"]
seed-paths: ["seeds"]
macro-paths: ["macros"]

target-path: "target"
clean-targets:
  - "target"
  - "dbt_packages"

models:
  minimercado_dbt:
    staging:
      +materialized: view
    intermediate:
      +materialized: view
    marts:
      +materialized: table
EOF

cat << 'EOF' > "${BASE_DIR}/dbt_project/profiles.yml"
minimercado:
  target: dev
  outputs:
    dev:
      type: duckdb
      path: "../data.duckdb"
      schema: main
EOF

# -----------------------------------------------------------------------------
# 4. Proyecto dbt - Archivos SQL y YAML Vacíos
# -----------------------------------------------------------------------------
# Staging (Modelos y Schemas)
touch "${BASE_DIR}/dbt_project/models/staging/stg_productos.sql"
touch "${BASE_DIR}/dbt_project/models/staging/stg_vendedores.sql"
touch "${BASE_DIR}/dbt_project/models/staging/stg_compras.sql"
touch "${BASE_DIR}/dbt_project/models/staging/stg_ventas.sql"
touch "${BASE_DIR}/dbt_project/models/staging/schema.yml"

# Intermediate
touch "${BASE_DIR}/dbt_project/models/intermediate/int_movimientos_stock.sql"
touch "${BASE_DIR}/dbt_project/models/intermediate/schema.yml"

# Marts (Modelos y Schemas)
touch "${BASE_DIR}/dbt_project/models/marts/mart_ventas_diarias.sql"
touch "${BASE_DIR}/dbt_project/models/marts/mart_rentabilidad_productos.sql"
touch "${BASE_DIR}/dbt_project/models/marts/mart_rotacion_inventario.sql"
touch "${BASE_DIR}/dbt_project/models/marts/mart_desempeno_vendedores.sql"
touch "${BASE_DIR}/dbt_project/models/marts/schema.yml"

# Tests SQL personalizados para dbt
touch "${BASE_DIR}/dbt_project/tests/assert_ventas_positivas.sql"

# -----------------------------------------------------------------------------
# 5. Archivos de Orquestación (Dagster)
# -----------------------------------------------------------------------------
touch "${BASE_DIR}/orchestration/__init__.py"
touch "${BASE_DIR}/orchestration/definitions.py"

echo "Todos los archivos y carpetas fueron creados exitosamente."