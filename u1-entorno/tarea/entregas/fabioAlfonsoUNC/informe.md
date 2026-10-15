# Informe de unidad

## Unidad U1: mi primer aporte reproducible

**Nombre:** Fabio Cesar Alfonso Nuñez

**Fecha:** 15 de octubre de 2026

**Tag de cierre:** `u1-completa`

---

### Entorno
Para el desarrollo de la unidad configuré un entorno reproducible basado en GitHub Codespaces a partir del fork del repositorio `curso-datos`. La utilización de un contenedor Dev Container garantizó paridad de dependencias del sistema y versiones de herramientas. Verifiqué la correcta inicialización ejecutando el script `python u1-entorno/tarea/verificar_entorno.py`, el cual comprobó la instalación del intérprete de Python, el formateador y linter Ruff, y el framework de pruebas Pytest, concluyendo de manera exitosa con el mensaje de estado `OK`.

### Flujo de Git
Implementé un flujo de control de versiones disciplinado siguiendo las directrices del curso. Creé la rama local `u1/fabioAlfonsoUNC` para aislar los cambios del historial principal. Registré el avance mediante commits atómicos y descriptivos en tiempo imperativo, documentando el propósito de cada cambio: preparación de la carpeta de entrega, correcciones de formato y estilo, solución del bug funcional y desarrollo de pruebas unitarias. Finalmente, generé el tag anotado `u1-completa` sobre el último commit y preparé el Pull Request dirigido al repositorio upstream del curso, asegurando tocar únicamente la ruta `entregas/fabioAlfonsoUNC/`.

### Que se hizo
Comencé copiando el archivo base `ejercicio.py` a mi directorio personal de entrega. A continuación, ejecuté `ruff check --fix` y `ruff format` para resolver automáticamente inconsistencias de estilo bajo lineamientos de PEP 8. Realicé correcciones manuales en imports no utilizados, funciones nombradas en CamelCase y captura de excepciones generales. Posteriormente, corregí el bug lógico en la función de acumulación de ventas y construí el archivo `test_ejercicio.py` con una suite de pruebas en Pytest que evalúa el camino feliz y casos de borde.

### Una decisión de diseño, explicada
En la función `resumen_por_marca`, la firma original utilizaba un diccionario vacío como argumento por defecto (`acumulado={}`). En Python, las estructuras de datos mutables por defecto se instancian una sola vez al cargar la función. Decidí sustituirlo por el patrón centinela idiomático `acumulado=None`, incorporando la validación interna `if acumulado is None: acumulado = {}`. Esta decisión preserva la ergonomía de la función sin generar efectos colaterales indeseados.

### Un problema que apareció
Al ser mi primera experiencia con Ruff, asumí inicialmente que cambiar la firma a `acumulado=None` bastaba para resolver la advertencia. Sin embargo, al invocar la función con el valor por defecto, falló con `TypeError: 'NoneType' object does not support item assignment` porque faltaba inicializar el diccionario dentro de la función. Además, `ruff format --check` reportó discrepancias debidas a caracteres invisibles y espacios no rompibles copiados al editar. Lo solucioné inicializando la variable, ejecutando el formateador directamente y escribiendo pruebas que verifican llamadas sucesivas independientes.

### Reflexión
Esta unidad demostró que los linters estáticos no son simples verificadores de formato visual, sino herramientas críticas de inspección estática que detectan antipatrones donde suelen camuflarse errores funcionales reales. Con más tiempo, implementaría hooks de pre-commit automatizados para ejecutar Ruff y Pytest antes de registrar cada commit, además de parametrizar las pruebas unitarias para cubrir una gama más exhaustiva de datos malformados en fechas y descripciones.

### Ayudas externas
Utilicé asistencia de inteligencia artificial como soporte de consulta técnica para interpretar las advertencias de Ruff, profundizar en el comportamiento de argumentos mutables en memoria, sugerir escenarios de prueba para casos de borde y estructurar la redacción técnica de este informe, validando y probando cada solución de manera manual en mi entorno.