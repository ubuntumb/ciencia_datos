# Informe U1: mi primer aporte reproducible

**Nombre:** Jesús López
**Usuario de GitHub:** Jelosoft-dev
**Nombre de carpeta en entregas:** Jelosoft-dev
**Fecha:** 14/10/2026

## Entorno

Hice un fork del repositorio del curso y lo abrí en GitHub Codespaces. El contenedor se construye a partir de `.devcontainer/Dockerfile`, que parte de una imagen oficial de Python 3.12 e incluye `uv`. Al crearse, el Codespace ejecuta `uv sync --all-groups`, que instala las dependencias del proyecto y las de desarrollo (pytest y ruff).

Después ejecuté el script de verificación:

```
uv run python u1-entorno/tarea/verificar_entorno.py
```

```
Entorno: GitHub Codespaces
Python: 3.12.11
pytest: 9.1.1
ruff: 0.16.10
pre-commit: 4.7.0
git: git version 2.50.1

OK
```

Lo que hace reproducible este entorno es el archivo `uv.lock`. Allí quedan fijadas las versiones exactas de cada paquete, incluidas las dependencias indirectas. Con `uv sync --locked`, que es lo que ejecuta GitHub Actions al abrir el PR, cualquier persona instala exactamente las mismas versiones que yo. Si el lock no coincidiera con `pyproject.toml`, el comando fallaría en lugar de instalar algo distinto. Así se evita el típico "en mi máquina funciona".

## Flujo de Git

Trabajé en la rama `u1/Jelosoft-dev`, creada desde `main`, y solo modifiqué archivos dentro de mi carpeta de entrega. Separé el trabajo en commits pequeños para que cada uno tuviera un único propósito y se pudiera revisar o revertir por separado.

Finalmente abrí el pull request hacia el repositorio del curso, no hacia mi fork, completando la descripción con lo que cambié y cómo lo verifiqué.

## Un problema

Ruff marcó la advertencia B006 en `resumen_por_marca(ventas, acumulado={})`. Al principio parecía solo un detalle de estilo, pero era un error real. En Python, el valor por defecto se evalúa una sola vez, cuando se define la función. Por eso el mismo diccionario se reutiliza en todas las llamadas que no pasan `acumulado`, y cada llamada sigue sumando sobre los totales de la anterior.

Lo comprobé con una prueba: llamar dos veces a la función con una venta de Ford por 100 debería devolver `{"Ford": 100.0}`, pero el código original devolvía 200. La solución fue usar `acumulado=None` y crear el diccionario dentro de la función. Ejecuté mis pruebas contra el archivo original y fallaron dos: la de llamadas repetidas y la de lista vacía, que devolvía datos de llamadas anteriores. Con la corrección pasan las nueve.

También tuve que decidir qué excepciones capturar en `descripcion_venta`. Un `except` sin tipo atrapa cualquier error, incluso uno de programación, y lo esconde. Elegí `KeyError`, `TypeError` y `ValueError`, que son los errores esperables si el precio falta o no es un número.

## Reflexión

Aprendí que un linter no sirve solo para el estilo: una de sus advertencias señalaba un bug que no se ve leyendo el código por encima. También entendí para qué sirven las pruebas de casos borde. La prueba con una lista vacía parece trivial, pero falló con el código original. Trabajar en una rama con commits pequeños me obligó a pensar qué cambiaba en cada paso y por qué.

## Ayudas externas

Usé Claude, un asistente de IA de Anthropic, para orientarme sobre los pasos de la tarea y mejorar la redacción de este informe. Revisé y ejecuté todo el código entregado.
