# Informe Tarea U1

**Alumna:** Lourdes Molinas
**Fecha:** 16/10/2026

## Entorno

Para empezar hice un fork del repositorio del curso, o sea, una copia en mi propia cuenta de GitHub. Después lo abrí en un Codespace que ya viene preparada con todo lo que necesita el curso.

Cuando corrí el verificador por primera vez no me dio OK: me decía que faltaban pytest, ruff y pre-commit. Lo pude resolver y al final me salió esto:

```
Entorno: GitHub Codespaces
Python: 3.12.11
pytest: 9.1.1
ruff: 0.16.10
pre-commit: 4.7.0
git: git version 2.50.1

OK
```

Nunca había usado GitHub antes, así que al principio me costó entender la diferencia entre mi fork y el repositorio del profesor.

## Flujo de Git

Creé una rama llamada `u1/5389410-lang` para no tocar `main`, y trabajé solamente dentro de mi carpeta de entregas. Fui guardando el trabajo en commits chicos, cada uno con un mensaje que dice para qué sirve el cambio:

1. Copié el ejercicio original, así se puede ver después qué fue lo que cambié.
2. Corregí los errores de estilo con ruff y arreglé el error de `resumen_por_marca`.
3. Agregué las pruebas con pytest.
4. Agregué este informe.

Algo que aprendí es a usar `git add` con el nombre exacto de cada archivo y no `git add .`. El entorno me había modificado solo el archivo `uv.lock` y no quería que se metiera en mi entrega, porque el pull request solo puede tocar mi carpeta. Al final subí la rama con `git push` y abrí el pull request.

## Un problema que apareció

El primer problema fue con el entorno. El verificador decía que instalara lo que faltaba con `requirements.txt`, pero ese archivo no está en el repositorio. Primero ejecuté `uv sync --all-groups`, que instaló pytest y ruff, y después instalé pre-commit aparte con `uv pip install pre-commit`, porque no está en la lista del proyecto. Me di cuenta de que el orden importa: si hago `uv sync` después, pre-commit se borra.

El segundo problema fue en el código, y es el que más me sorprendió. Ruff marcó un aviso en `resumen_por_marca(ventas, acumulado={})`. Yo pensé que era solo de estilo, pero en realidad era un error: Python crea ese diccionario vacío una sola vez y lo vuelve a usar cada vez que llamás a la función. Entonces, si la llamás dos veces, la segunda vez suma también lo de la primera y el resultado sale mal. Lo arreglé poniendo `None` como valor por defecto y creando el diccionario adentro de la función. Para comprobarlo hice una prueba que llama dos veces a la función y revisa que el total no se acumule. Con el código original esa prueba falla y con mi arreglo pasa.

También me equivoqué yo: creé el archivo de pruebas sin el `.py` al final y pytest no lo encontraba. Lo renombré con `git mv` y corregí el commit con `git commit --amend`.

## Reflexión

En `descripcion_venta` cambié el `except:` solo por `except (ValueError, TypeError):`. Lo decidí así porque esos son los errores que pueden pasar si el precio viene mal escrito o vacío, y no quería que la función escondiera cualquier otro error que sí habría que ver.

Lo que más me quedó de esta tarea es que ruff no sirve solo para que el código se vea prolijo, sino que también puede avisar de errores de verdad. Y entendí para qué sirve trabajar todos en el mismo entorno: si el profesor abre mi trabajo en el contenedor, le tiene que dar lo mismo que a mí.

## Ayudas externas

Como era mi primera vez con GitHub, usé Claude como guía. Me explicó qué es un fork, una rama, un commit y un pull request.
