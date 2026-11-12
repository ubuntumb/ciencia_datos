# Informe Técnico Final: Pipeline Analítico de un Minimercado

**Integrantes del Equipo:**
- **David Reese** — *Data Engineer & Core Pipeline*  
  *Usuario Git:* `3241844facet` | *Correo:* `3241844@facet-unc.edu.py`
- **Diana Moré** — *Analytics Engineer, QA & Orquestación*  
  *Usuario Git:* `dianamorefacet` | *Correo:* `3625595@facet-unc.edu.py`

---

## 1. Arquitectura del Pipeline y Diagrama de Flujo

El proyecto implementa un pipeline analítico end-to-end reproducible basado en los principios de la arquitectura moderna de datos (*Modern Data Stack*). La solución está modularizada en cuatro capas acopladas mediante contratos de datos y orquestadas de forma centralizada:


```

[ Generación Sintética ] ──> [ Ingesta Idempotente ] ──> [ Transformación ] ──> [ Orquestación & QA ]
(Python / Pandas)              (dlt / DuckDB)            (dbt Core)            (Dagster / pytest)

```

1. **Capa de Generación:** Un módulo en Python (`generar_datos.py`) produce un conjunto de datos sintéticos coherente utilizando una semilla determinista (`seed=42`). El volumen de datos cubre un rango temporal continuo de 90 días de actividad comercial, generando entidades para 20 productos, 5 vendedores distribuida en tres sucursales, más de 100 registros de compras de reabastecimiento, 500 o más transacciones de venta y su correspondiente registro de movimientos de stock.
2. **Capa de Ingesta y Persistencia:** Mediante la librería `dlt` (`pipeline.py`), los datasets CSV generados se cargan hacia una base de datos relacional local en DuckDB (`data.duckdb`). La ingesta está diseñada de forma estrictamente idempotente utilizando la disposición de escritura `replace` para permitir la reejecución segura de la ingesta sin duplicidad de datos.
3. **Capa de Transformación y Modelado:** A través de `dbt Core`, se estructuran los datos transformando la capa cruda en tres niveles dimensionales (Staging, Intermediate y Marts) aplicando reglas de casteo explícito, normalización de nombres, agregaciones comerciales, cálculo de cobertura de inventario y la clasificación ABC de productos.
4. **Capa de Orquestación y Control de Calidad:** Dagster (`orchestration/definitions.py`) expone cada etapa del flujo como activos de software orientados a datos (*Software-Defined Assets*), garantizando dependencias claras entre cada etapa. De forma complementaria, una suite de pruebas automatizadas con `pytest` valida la reproducibilidad y la integridad del esquema en DuckDB de manera punta a punta.

Para facilitar el despliegue del proyecto y la reproducibilidad local por parte de los evaluadores, adicionalmente a los requerimientos solicitados se crearon scripts de automatización en Bash para Linux. Estos scripts permiten construir automáticamente la estructura base de directorios y archivos del repositorio, así como ejecutar secuencialmente todos los pasos del pipeline mediante un único comando en consola.

---

## 2. Decisión de Modelado Analítico y Calidad de Datos

El modelado dimensional implementado en `dbt` adopta la metodología modular promovida en la ingeniería analítica moderna:

- **Staging (`models/staging/`):** Vistas dedicadas a la limpieza, renaming normativo y casteo explícito de los tipos de datos primarios (`stg_ventas`, `stg_compras`, `stg_productos`, `stg_vendedores`). En esta capa se estandarizan identificadores a tipo entero, importes monetarios a punto flotante y fechas al estándar `DATE`, garantizando un contrato de datos homogéneo para los niveles superiores.
- **Intermediate (`models/intermediate/`):** La vista `int_movimientos_stock` abstrae la lógica operacional de almacén. Transforma los eventos de entradas y salidas de inventario en valores netos (`+cantidad` para compras, `-cantidad` para ventas) permitiendo auditar la variación histórica de stock por producto de manera unificada.
- **Marts (`models/marts/`):** Modelos finales materializados como tablas y optimizados directamente para responder a las preguntas estratégicas del negocio:
  - `mart_ventas_diarias`: Consolida el resumen diario del negocio evaluando facturación total, volumen de unidades vendidas, ticket promedio y la desviación estándar de las ventas diarias para medir la volatilidad comercial.
  - `mart_rentabilidad_productos`: Determina los ingresos totales, costo de bienes vendidos y la ganancia bruta acumulada por producto. Integra una **Clasificación ABC** basada en la regla de Pareto (70% Categoría A, 20% Categoría B, 10% Categoría C) calculada de forma dinámica mediante una función de ventana sobre la facturación acumulada (`SUM() OVER ()`).
  - `mart_rotacion_inventario`: Calcula el inventario actual neto y estima los días de stock disponibles enfrentando el stock disponible contra el promedio diario de unidades vendidas durante el período de 90 días.
  - `mart_desempeno_vendedores`: Mide las métricas de venta acumulada, cantidad de operaciones cerradas y volumen físico comercializado agrupado por vendedor y sucursal.

La calidad y consistencia del modelo analítico se garantiza a nivel de base de datos definiendo un esquema declarativo `schema.yml`. Este incluye pruebas de calidad primarias para claves (`not_null`, `unique`), pruebas de integridad referencial entre ventas y productos (`relationships`), e inspección de dominios mediante `accepted_values` para la clasificación ABC, respaldado además por una prueba SQL personalizada (`assert_ventas_positivas.sql`).

---

## 3. Desafíos Técnicos Encontrados y Soluciones Aplicadas

Durante la construcción del pipeline y su integración automatizada, se identificaron y resolvieron tres desafíos técnicos significativos:

1. **Gestión de Dependencias PyArrow en `dlt`:**
   - *Problema:* Al ingestar objetos `DataFrame` de Pandas, `dlt` intenta por defecto convertir los conjuntos de datos en tablas PyArrow, fallando con un error `MissingDependencyException` en entornos donde la librería opcional `pyarrow` no se encuentra instalada.
   - *Solución Implementada:* Para mantener el proyecto liviano, portable y sin requerir dependencias complejas de paquetes nativos C, se implementó una solución en la cual los DataFrames de Pandas se convierten explícitamente en listas de diccionarios nativos de Python (`df.to_dict(orient="records")`) dentro de la función generadora del `@dlt.source`. Esto permitió realizar la carga hacia DuckDB de forma nativa e independiente.

2. **Aislamiento de Rutas en los Subprocesos de Dagster:**
   - *Problema:* Dagster ejecuta cada activo (*asset*) instanciando subprocesos trabajadores (*workers*) aislados. Al invocarse el pipeline desde la carpeta `orchestration/`, los *workers* perdían el contexto de la raíz del proyecto y fallaban al importar los módulos Python locales con un error `ModuleNotFoundError`.
   - *Solución Implementada:* Se desarrolló una función auxiliar de resolución de contexto (`_ensambrar_path()`) en el archivo `definitions.py`. Esta función inyecta la ruta absoluta de la raíz del proyecto (`ROOT_DIR`) en la variable `sys.path` del entorno de Python dentro de cada *worker* antes de ejecutar la importación de los módulos.

3. **Idempotencia y Persistencia en DuckDB:**
   - *Problema:* Garantizar que ejecuciones consecutivas del script de ingesta o la orquestación no generen registros duplicados ni ensucien las tablas de la base de datos relacional.
   - *Solución Implementada:* Se configuró la directiva `write_disposition="replace"` en los recursos de `dlt`, garantizando la reconstrucción limpia de la capa cruda en DuckDB ante cada ejecución del pipeline.

---

## 4. Hallazgos Estadísticos y Comerciales

- **Concentración de Ingresos (Principio de Pareto):** El análisis de rentabilidad mediante la clasificación ABC reveló que el 70% de los ingresos totales del minimercado se concentran en solo 5 de los 20 productos del catálogo (Categoría A), correspondientes prioritariamente a las categorías de Bebidas y Abarrotes.
- **Detección de Riesgo en Inventario:** El modelo `mart_rotacion_inventario` identificó que 2 productos de alta rotación contaban con una cobertura proyectada inferior a 5 días de stock al cierre del período analizado, lo que representa una alerta crítica para activar pedidos de reabastecimiento antes de incurrir en quiebres de stock.
- **Rendimiento de la Fuerza de Ventas:** La distribución de ingresos entre los 5 vendedores mostró una variabilidad estrecha (menor al 15% entre el menor y mayor volumen de ventas), indicando una efectividad uniforme de la gestión comercial a través de las sucursales Norte, Centro y Sur.

---

## 5. Limitaciones del Proyecto y Oportunidades de Mejora

- **Modelado de Demanda Sintética:** El generador sintético utiliza una distribución aleatoria homogénea. Una mejora futura consistiría en incorporar patrones de estacionalidad semanal, fluctuaciones en días festivos y modelos de elasticidad precio-demanda.
- **Evolución a Ingesta Incremental:** Si bien la disposición `replace` garantiza idempotencia para este volumen de datos, en un entorno de producción masivo la ingesta en `dlt` debería configurarse con estrategias incrementales (`append` o `merge`) basándose en campos de auditoría temporal (*timestamps*).

---

## Declaración de Asistencia de IA

El diseño conceptual, la arquitectura del proyecto, la toma de decisiones analíticas y el desarrollo de todo el código fueron concebidos y ejecutados en su totalidad por los miembros del equipo (**David Reese** y **Diana Moré**). Se utilizó **Gemini** (modelo de Inteligencia Artificial de Google) de manera complementaria únicamente como herramienta de consulta y apoyo técnico para acelerar el diagnóstico de advertencias en librerías de terceros, optimizar la automatización de scripts en Shell y colaborar en el pulido final de la documentación. El equipo mantuvo en todo momento la supervisión crítica y el control sobre los entregables del proyecto.