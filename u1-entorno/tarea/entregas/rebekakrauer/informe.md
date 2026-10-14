# Informe U1: mi primer aporte reproducible

**Nombre:** Rebeka Rojas

**Fecha:**12/10/2026

**Tag de cierre:** (por ejemplo, `u1-completa`)
 

### Entorno

Construí una entrega del trabajo a partir de un fork realizando los cambios dentro de una rama de la que hare pull request, el orden seguido fue: hacer el fork del repositorio original del curso y abrirlo en un Codeespace, el codeespace se armo solo a partir de la carpeta '.devcontainer': el Dockerfile instala Python 3.12 y la herramienta uv, y `devcontainer.json` ejecuta `uv sync --all-groups`, que instala las librerías en un entorno virtual (`.venv`). El archivo `uv.lock` fija las versiones exactas de cada librería. Activé el entorno con `source .venv/bin/activate` e instalé pre-commit a mano. Después `verificar_entorno.py` terminó con OK, con Python 3.12.11, pytest 9.1.1, ruff 0.16.10, pre-commit 4.6.2 y git 2.50.1.
El orden seguido fue: hacer el forck de repo original, abrir un codeespace, activar el entorno virtual(.venv), instalar pre-commit, ejecutar 'verificar_entorno.py, crear u1/miusuario a partir de main, una carpeta entregas/rebekrauer/ con una copia de ejercicios.py dentro, corregi dicha copia, 6 commits y el actual informe, finalmente lo que corre es u1-tarea.yml, la revision con ruff, pytest y validar_entrega.py.
Fnalmente lo que corre es u1-tarea.yml, la revision con ruff, pytest y validar_entrega.py.

### Flujo de Git

Creé la rama `u1/rebekakrauer` a partir de `main`, para que mi entrega no se mezclara con otros cambios, y una carpeta `entregas/rebekakrauer/` con una copia de `ejercicio.py`. Hice commits pequeños, cada uno con un solo propósito: primero la copia sin corregir, después las correcciones automáticas de ruff, el arreglo del error real, los avisos corregidos a mano, el cambio de nombre de una función, las pruebas, la prueba del error principal y el informe. Así el historial muestra qué cambió ruff y qué corregí yo. Cuando `uv.lock` apareció modificado sin que yo lo tocara, lo descarté con `git restore`, porque mi pull request solo puede tocar mi carpeta. Al abrir el pull request, GitHub ejecuta `u1-tarea.yml`: ruff, pytest y `validar_entrega.py`.

### Una decisión de diseño, explicada

En la función descripcion_venta use except (KeyError, TypeError, ValueError) y no 'except:' ni 'except Exception'.Porque asi se atrapan solo los 3 fallos que se esperan para los que el 0 es una respuesta razonable(no tiene sale_price, el precio es None u otro que no se puede convertir, o el precio no es un numero). Cualquier otro error significa que algo más está mal, y es mejor que se vea que taparlo con un 0 silencioso.

### Un problema

Luego de activar el entorno y ejecutar verificar_entorno.py me salia que faltaba pre-commit. Probe ejecutar 'pip install -r requirements.txt' pero me retorno 'No such file' luego me percate que el repositorio usa pyproject.toml y uv.lock, no requirements.txt como decia en el README original que fue corregido, pero pre.commit tampoco esta en la lista de dependencias de pyproject.toml, asi que ejecute uv pip install pre-commit y luego la verificacion me retorno OK.

### Reflexión  

Instalé pre-commit a mano porque el repositorio no lo declara, y ese paso no queda registrado para nadie más. Con más tiempo agregaria a la lista de dependencias del proyecto. No lo hice dentro de mi entrega porque el pull request solo puede tocar mi carpeta.

### Ayudas externas

Ayuda de un asistente de IA para entender algunos fragmentos.