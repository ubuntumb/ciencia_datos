import dlt
import requests

REST_COUNTRIES = "https://api.restcountries.com/countries/v5/codes.alpha_3"
AUTH = "rc_live_fc8ae2f68e3841d8b39eab761765684f"
URL_CLIMA = "https://api.open-meteo.com/v1/forecast?"
CODIGOS_ISO = ["ARG", "BRA", "PRY"]


def _extraer_paises() -> list[dict]:
    paises = []
    for codigo in CODIGOS_ISO:
        respuesta = requests.get(
            f"{REST_COUNTRIES}/{codigo}",
            timeout=15,
            headers={"Authorization": f"Bearer {AUTH}"},
        )
        respuesta.raise_for_status()
        paises.extend(respuesta.json()["data"]["objects"])
    return paises


def _transformar_pais(raw: dict) -> dict:

    capitales = raw.get("capitals") or []
    capital = next(
        (c for c in capitales if c.get("attributes", {}).get("primary")),
        capitales[0] if capitales else {},
    )

    coords = capital.get("coordinates") or {}

    return {
        "codigo_iso": raw["codes"]["alpha_3"],
        "nombre_pais": raw["names"]["common"],
        "capital": capital.get("name"),
        "latitud_capital": coords.get("lat"),
        "longitud_capital": coords.get("lng"),
        "poblacion": raw.get("population"),
    }


def _consultar_clima(pais: dict) -> dict | None:

    lat, lon = pais.get("latitud_capital"), pais.get("longitud_capital")

    if lat is None or lon is None:
        return None

    respuesta = requests.get(
        URL_CLIMA,
        params={"latitude": lat, "longitude": lon,
                "current": "temperature_2m"},
        timeout=10,
    )

    respuesta.raise_for_status()
    data = respuesta.json()
    actual = data.get("current", {})
    unidad = data.get("current_units", {})

    return {
        "codigo_iso": pais["codigo_iso"],
        "capital": pais["capital"],
        "temperatura_actual": actual.get("temperature_2m"),
        "unidad_temperatura": unidad.get("temperature_2m", "°C"),
        "fecha_hora_medicion": actual.get("time"),
    }


@dlt.resource(
        name="paises", 
        write_disposition="replace")
def obtener_paises():
    """Recurso atómico para extraer países de la API."""

    for raw in _extraer_paises():
        yield _transformar_pais(raw)


@dlt.transformer(data_from=obtener_paises, name="clima_capitales", write_disposition="append")
def obtener_clima(pais):
    """Transformador: clima actual según las coordenadas de la capital."""
    registro = _consultar_clima(pais)
    if registro:
        yield registro
