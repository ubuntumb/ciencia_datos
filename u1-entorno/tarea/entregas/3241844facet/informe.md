# Informe de unidad -- plantilla

Informe técnico acotado para el cierre de cada unidad

---

## Unidad: U1: Mi primer aporte reproducible

**Nombre:** David Helmut Reese Molinas

**Usuario GitHub:** 3241844facet

**Fecha:** 18 de Octubre de 2026

**Tag de cierre:** `u1-completa`

---

### Qué se hizo

En esta primera unidad configuré un entorno de desarrollo reproducible, corregí errores de estilo y bugs lógicos en
código legacy de Python, redacté un conjunto de pruebas automatizadas con Pytest y gestioné el flujo completo de
contribución mediante Git y GitHub.

El trabajo se ejecutó en el siguiente orden secuencial:

1. **Entorno reproducible:** Realicé un fork del repositorio `curso-datos` y creé un entorno GitHub Codespaces en un
Dev Container. Activé el entorno virtual preconfigurado e introduje la verificación ejecutando
`python u1-entorno/tarea/verificar_entorno.py`, confirmando el estado `OK`.
2. **Creación del espacio de trabajo:** Creé la rama de trabajo `u1/3241844facet` y preparé la carpeta de entrega en
`u1-entorno/tarea/entregas/3241844facet/`, copiando allí el archivo original `ejercicio.py`.
3. **Refactorización con Ruff:** Ejecuté las herramientas de lintering y formateo automático mediante
`ruff check --fix` y `ruff format`. Corregí los problemas mecánicos de formato y resolví manualmente las
advertencias lógicas, incluyendo el uso de argumentos mutables por defecto.
4. **Pruebas unitarias:** Creé el archivo `test_ejercicio.py` utilizando el framework `pytest`. Diseñé casos de prueba
para el comportamiento estándar (happy path) y casos borde (edge cases), enfocándome en validar la independencia del
acumulador mutable.
5. **Aporte al repositorio:** Realicé tres commits pequeños explicativos siguiendo buenas prácticas de Git y abrí el
Pull Request desde mi rama hacia la rama principal del repositorio original del curso.

Al final del flujo, la ejecución del comando `pytest` pasa el 100% de las pruebas automatizadas y la verificación del
entorno concluye sin errores.

---

### Una decisión de diseño, explicada

Elegí estructurar la prueba de caso borde en `test_ejercicio.py` para evaluar de manera explícita la mutabilidad
acumulativa en la función `resumen_por_marca`, en lugar de solo probar un caso de uso estático aislado.

La función original definía `def resumen_por_marca(ventas, acumulado={}):`. En Python, las estructuras mutables
pasadas como argumento por defecto se evalúan una sola vez al definir la función. Si se llama a la función en
múltiples ocasiones consecutivas omitiendo el argumento `acumulado`, el estado del diccionario se conserva entre
invocaciones, provocando contaminación cruzada de datos (data leakage) e inconsistencias en los resultados calculados.

En lugar de limitarme a pasar una lista con ventas y verificar el resultado de una única llamada, diseñé la prueba
`test_resumen_por_marca_llamadas_sucesivas_no_contaminar_acumulado`. Esta prueba invoca la función dos veces
consecutivas con conjuntos de ventas totalmente distintos. Al asertar que el resultado de la segunda llamada no
contiene las marcas de la primera, obligué a que la suite de pruebas fallara activamente con el código defectuoso
original. Esto garantizó que la posterior refactorización a `acumulado=None` fuera verificable e indispensable para
la aprobación de la entrega.

---

### Un problema que apareció

Durante el proceso, `ruff check --fix` corrigió automáticamente múltiples errores de estilo (como espacios alrededor
de operadores, importaciones no utilizadas y espacios entre funciones), pero el comando `pytest` continuaba
ejecutándose con éxito en las pruebas iniciales sin detectar anomalías visibles en `descripcion_venta`.

Al revisar detalladamente la advertencia `B001` de Ruff (`Do not use bare except`), noté que la función
`descripcion_venta` capturaba cualquier excepción genérica con un `except:` absoluto. Esto enmascaraba fallos
graves de ejecución, tales como la ausencia de claves obligatorias (`KeyError`) o interrupciones de teclado
(`KeyboardInterrupt`), transformando erróneamente cualquier excepción en un precio con valor cero (`$0`).

Lo resolví refactorizando manualmente el bloque de manejo de excepciones para capturar únicamente `ValueError`, que es
la excepción esperada al intentar convertir cadenas no numéricas mediante `float()`. Adicionalmente, agregué un caso
de prueba en `test_ejercicio.py` especificando una cadena no numérica (`"sale_price": "No disponible"`) para asegurar
que el bloque manejara correctamente el error de conversión esperado sin silenciar otros fallos del sistema.

---

### Qué harías distinto con más tiempo

Con más tiempo, implementaría la validación de esquemas de datos mediante bibliotecas especializadas como `Pydantic`
o usando tipado estático con `mypy`. Actualmente, las funciones asumen que los diccionarios de venta contienen
obligatoriamente las claves `'car_make'`, `'car_model'` y `'sale_price'`. Si una estructura llega incompleta o con un
formato diferente, el código falla en tiempo de ejecución y lanza un `KeyError`. Validar la estructura de entrada
desde el inicio garantizaría un código significativamente más robusto ante datos ambiguos o corruptos.