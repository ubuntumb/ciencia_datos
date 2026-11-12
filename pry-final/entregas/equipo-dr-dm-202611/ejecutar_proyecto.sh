#!/bin/bash

# ==============================================================================
# Script de Ejecución End-to-End del Pipeline Analítico
# Autores: David Reese & Diana Moré
# ==============================================================================

# Detener la ejecución si ocurre un error inesperado
set -e

# Silenciar advertencias de Python en todo el script
export PYTHONWARNINGS="ignore"

echo "======================================================================"
echo "INICIANDO EJECUCIÓN DEL PIPELINE DE DATOS - MINIMERCADO"
echo "======================================================================"
echo ""

# ------------------------------------------------------------------------------
# Paso 0: Verificación y Limpieza Previa de Artefactos Generados
# ------------------------------------------------------------------------------
EXISTEN_ARTEFACTOS=false

# 1. Validar si existen archivos generados DENTRO de la carpeta data/
if [ "$(ls -A data 2>/dev/null)" ]; then
    EXISTEN_ARTEFACTOS=true
fi

# 2. Validar archivos o directorios de salidas y cachés de ejecuciones previas
ARTEFACTOS_RUTAS=(
  "data.duckdb"
  "data.duckdb.wal"
  ".dlt"
  "dbt_project/target"
  "dbt_project/dbt_packages"
  "dbt_project/logs"
  ".pytest_cache"
  ".dagster"
)

for art in "${ARTEFACTOS_RUTAS[@]}"; do
    if [ -e "$art" ]; then
        EXISTEN_ARTEFACTOS=true
        break
    fi
done

# 3. Verificación de archivos .pyc o carpetas __pycache__ en todo el proyecto
if [ "$EXISTEN_ARTEFACTOS" = false ]; then
    if find . -type d -name "__pycache__" -o -type f -name "*.pyc" | read -r; then
        EXISTEN_ARTEFACTOS=true
    fi
fi

# 4. Verificación de temporales de Dagster
if [ "$EXISTEN_ARTEFACTOS" = false ]; then
    if ls .tmp_dagster_home_* 1> /dev/null 2>&1; then
        EXISTEN_ARTEFACTOS=true
    fi
fi

if [ "$EXISTEN_ARTEFACTOS" = true ]; then
    echo "Se detectaron archivos de ejecuciones anteriores (archivos en data/, .duckdb, target, etc.)."
    read -p "Deseas eliminar todos los artefactos previos antes de continuar? (s/N): " RESPUESTA_LIMPIEZA
    echo ""

    if [[ "$RESPUESTA_LIMPIEZA" =~ ^[Ss]$ ]]; then
        echo "Limpiando artefactos previos..."

        # Vaciar el contenido de data/ pero manteniendo la carpeta creada
        rm -rf data/*

        # Eliminar base de datos e ingesta dlt
        rm -f data.duckdb data.duckdb.wal
        rm -rf .dlt/

        # Artefactos de compilación y ejecución de dbt
        rm -rf dbt_project/target/
        rm -rf dbt_project/dbt_packages/
        rm -rf dbt_project/logs/

        # Cachés de Python, Pytest y Dagster
        find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
        find . -type f -name "*.pyc" -delete 2>/dev/null || true
        rm -rf .pytest_cache/
        rm -rf .dagster/
        rm -rf .tmp_dagster_home_* 2>/dev/null || true

        echo "Limpieza profunda completada (la carpeta 'data/' se conserva vacía)."
        echo ""

        read -p "Deseas continuar con la ejecución del pipeline? (s/N): " RESPUESTA_CONTINUAR
        echo ""
        if [[ ! "$RESPUESTA_CONTINUAR" =~ ^[Ss]$ ]]; then
            echo "Ejecución finalizada por el usuario. El entorno ha quedado limpio."
            exit 0
        fi
    else
        echo "Continuando la ejecución conservando los artefactos existentes."
        echo ""
    fi
fi

# ------------------------------------------------------------------------------
# Paso 1: Generación de Datos Sintéticos
# ------------------------------------------------------------------------------
echo "[Paso 1/5] Generando datos sintéticos reproducibles..."
python generar_datos.py
echo "Datos sintéticos creados exitosamente en la carpeta 'data/'."
echo ""

# ------------------------------------------------------------------------------
# Paso 2: Ingesta e Idempotencia con dlt y DuckDB
# ------------------------------------------------------------------------------
echo "[Paso 2/5] Ejecutando pipeline de ingesta idempotente con dlt hacia DuckDB..."
python pipeline.py
echo "Archivos CSV cargados correctamente en 'data.duckdb'."
echo ""

# ------------------------------------------------------------------------------
# Paso 3: Transformación y Modelado con dbt
# ------------------------------------------------------------------------------
echo "[Paso 3/5] Ejecutando modelos y pruebas de calidad con dbt..."
cd dbt_project

echo "Corriendo modelos dbt (Staging, Intermediate, Marts)..."
dbt --warn-error-options '{"silence_executions": ["MissingArgumentsPropertyInGenericTestDeprecation"]}' run --profiles-dir .

echo "Ejecutando pruebas de integridad y calidad en SQL (schema.yml)..."
dbt --warn-error-options '{"silence_executions": ["MissingArgumentsPropertyInGenericTestDeprecation"]}' test --profiles-dir .

cd ..
echo "Transformaciones de dbt finalizadas sin errores."
echo ""

# ------------------------------------------------------------------------------
# Paso 4: Pruebas Automatizadas End-to-End con Pytest
# ------------------------------------------------------------------------------
echo "[Paso 4/5] Ejecutando suite de pruebas unitarias e integración (pytest)..."
pytest test_pipeline.py -v
echo "Todas las pruebas automatizadas pasaron satisfactoriamente."
echo ""

# ------------------------------------------------------------------------------
# Paso 5: Verificación de Orquestación con Dagster
# ------------------------------------------------------------------------------
echo "[Paso 5/5] Validando definición de assets de Dagster..."
export PYTHONPATH=$(pwd):$PYTHONPATH
python -W ignore -m dagster asset materialize --select "*" -f orchestration/definitions.py
echo "Assets de Dagster materializados y verificados."
echo ""

echo "======================================================================"
echo "PIPELINE COMPLETO EJECUTADO CON ÉXITO!"
echo "======================================================================"