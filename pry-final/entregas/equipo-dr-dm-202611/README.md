# Pipeline Analítico de Minimercado — Modern Data Stack

Proyecto integrador que implementa un pipeline ETL/ELT analítico end-to-end reproducible utilizando herramientas modernas de ingeniería y analítica de datos (**Python, dlt, DuckDB, dbt, Dagster y Pytest**).

---

## Integrantes del Equipo
* **David Reese** — *Data Engineer* (Generación sintética, ingesta idempotente con `dlt`, integración con `DuckDB`).
* **Diana Moré** — *Analytics Engineer & QA* (Modelado dimensional con `dbt`, orquestación con `Dagster`, pruebas automatizadas con `pytest`, informe técnico).

---

## Requisitos Previos
* **Python:** 3.10 o superior (recomendado 3.11)
* **Git**
* Entorno basado en Linux / macOS (o WSL2 en Windows)

---

## Guía de Instalación y Ejecución Paso a Paso
### 1. Entorno e Instalación de Dependencias
Crea y activa un entorno virtual de Python e instala las dependencias del proyecto:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install uv
uv sync
```

### 2. Generación de Datos Sintéticos
Produce los conjuntos de datos de prueba deterministas (90 días de actividad comercial) en la carpeta `data/`:

```bash
python generar_datos.py
```

### 3. Ingesta a DuckDB con `dlt`
Carga de forma idempotente los archivos CSV generados hacia la base de datos relacional local `data.duckdb`:

```bash
python pipeline.py
```

### 4. Transformaciones y Pruebas con `dbt`
Ejecuta los modelos analíticos (Staging, Intermediate y Marts) junto con la suite de pruebas de integridad SQL:

```bash
cd dbt_project
dbt --warn-error-options '{"silence_executions": ["MissingArgumentsPropertyInGenericTestDeprecation"]}' run --profiles-dir .
dbt --warn-error-options '{"silence_executions": ["MissingArgumentsPropertyInGenericTestDeprecation"]}' test --profiles-dir .
cd ..
```

### 5. Suite de Pruebas Automatizadas (`pytest`)
Valida la reproducibilidad global del pipeline y la estructura de la base de datos:

```bash
pytest test_pipeline.py -v
```

### 6. Orquestación y Visualización con Dagster
Materializa los activos de datos o inicia la interfaz gráfica interactiva de Dagster:

```bash
# Materialización por línea de comandos
export PYTHONPATH=$(pwd):$PYTHONPATH
python -W ignore -m dagster asset materialize --select "*" -f orchestration/definitions.py
```

---
## Ejecución Automática (Script Shell)

Para facilitar el despliegue y simplificar el proceso de evaluación, se incluye el script Bash `ejecutar_proyecto.sh`. Este script automatiza secuencialmente la ejecución de los 5 pasos del pipeline con reportes en consola de cada etapa.

Para ejecutar todo el pipeline de principio a fin de manera automática, corre los siguientes comandos desde la raíz del proyecto:

```bash
chmod +x ejecutar_proyecto.sh
./ejecutar_proyecto.sh
```