# Tarea U1: mi primer aporte reproducible

Configurarás un entorno reproducible, harás tu primer pull request al repositorio
del curso y explicarás lo que hiciste en un informe de 500 a 700 palabras.

## Qué se requiere realizar

1. **Fork y entorno.** Haz un fork de `curso-datos` y ábrelo en un Codespace (o en
   un Dev Container local si se agotó tu cuota). Ejecuta
   `python u1-entorno/tarea/verificar_entorno.py`. Debe terminar con `OK`.
2. **Un cambio de entorno, solo en tu fork.** Agrega una librería con versión fija a
   `requirements.txt`, reconstruye el contenedor y comprueba la versión con
   `pip show`. Anota el enlace a tu commit para el informe.
3. **Arregla el ejercicio.** Copia `ejercicio.py` a
   `entregas/<tu-usuario>/`. Tiene errores de estilo a propósito. Corrígelos con
   `ruff check --fix` y `ruff format`; lo que `ruff` no arregle solo, hazlo a mano.
   Las funciones deben seguir haciendo lo que su descripción dice.
4. **Escribe pruebas.** En la misma carpeta crea `test_ejercicio.py` con al menos
   dos pruebas de `pytest`, una de ellas con un caso borde.
5. **Trabaja con Git como se pide.** Crea la rama `u1/<tu-usuario>` y haz al menos
   tres commits pequeños, con mensajes que expliquen el porqué del cambio.
6. **Abre el pull request** al repositorio del curso (no a tu fork), con la
   plantilla de descripción. Debe tocar únicamente `entregas/<tu-usuario>/`.
7. **Escribe el informe.** Copia `informe_plantilla.md` como `informe.md` en tu
   carpeta de entrega y complétalo.

## Qué contiene tu carpeta de entrega

```
u1-entorno/tarea/entregas/<tu-usuario>/
├── ejercicio.py        # corregido
├── test_ejercicio.py   # tus pruebas
└── informe.md          # 500 a 700 palabras
```

## Cómo revisar tu trabajo antes de entregar

Desde la raíz del repositorio, con tu usuario en lugar de `<usuario>`:

```bash
ruff check u1-entorno/tarea/entregas/<usuario>
ruff format --check u1-entorno/tarea/entregas/<usuario>
pytest u1-entorno/tarea/entregas/<usuario>
python u1-entorno/tarea/validar_entrega.py --usuario <usuario> --base origin/main
```

Al abrir el PR, GitHub ejecuta estas mismas comprobaciones.

## Criterios de aceptación

- `verificar_entorno.py` termina con `OK` dentro del contenedor.
- `ruff check` no reporta errores en tu carpeta.
- `pytest` pasa con al menos dos pruebas.
- El PR tiene tres commits o más y toca solo tu carpeta.

## Puntos de evaluación (100 puntos)

| Criterio | Puntos |
| --- | --- |
| Entorno reproducible: verificación en verde y dependencia fijada | 25 |
| Flujo de Git: rama, commits claros y PR bien descrito | 30 |
| Calidad del código: `ruff` y `pytest` en verde | 20 |
| Informe: claro, con evidencias y reflexión propia | 25 |

Un trabajo que no se puede reproducir desde cero en el contenedor pierde la mitad
de los puntos de calidad del código.

## Reglas

- Trabajo individual. Puedes consultar documentación, foros y herramientas de IA:
  decláralo en el informe y asegúrate de poder explicar cada línea que entregas.
- No subas claves ni datos personales.
