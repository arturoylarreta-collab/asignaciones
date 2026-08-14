import re
import requests
from bs4 import BeautifulSoup


def extraer_estatus_epay(phpsessid: str, url: str = "https://epay.uno/reportes.php") -> dict:
    """Extrae el estatus de las máquinas registradas en epay.uno.

    :param phpsessid: ID de la sesión activa de PHP (necesario si la vista requiere login).
    :param url: URL del reporte de estatus de epay.uno.
    :return: Diccionario con el código de máquina como clave y sus detalles como valor.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }
    
    cookies = {
        "PHPSESSID": phpsessid
    }

    try:
        response = requests.get(url, headers=headers, cookies=cookies, timeout=15)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"❌ Error al consultar epay.uno: {e}")
        return {}

    soup = BeautifulSoup(response.text, "html.parser")
    resultado = {}

    # Seleccionamos las celdas o tarjetas del panel
    # epay.uno renderiza las máquinas dentro de celdas <td> o divs en la cuadrícula de reportes
    tarjetas = soup.find_all(["td", "div"], style=True)

    for tarjeta in tarjetas:
        texto = tarjeta.get_text(separator="\n", strip=True)
        if not texto:
            continue

        style = tarjeta.get("style", "").lower()
        class_attr = " ".join(tarjeta.get("class", [])).lower()

        # 1. Determinación de estado (Rojo/Inactivo vs Verde/Activo)
        es_inactivo = (
            "inactivo" in texto.lower() or
            "background-color: red" in style or
            "#f87171" in style or  # Tonos rojos hex comunes
            "#ef4444" in style or
            "danger" in class_attr
        )

        estado = "INACTIVA" if es_inactivo else "ACTIVA"

        # 2. Extracción del Código de Máquina (ej: C03-CMDLT, C09-CCAS17, V07-CASH09)
        # Patrón Regex: Letra + Números + Guion + Nombre de ubicación/código
        match_codigo = re.search(r"([A-Z]\d{2}-[A-Z0-9]+)", texto)

        if match_codigo:
            codigo = match_codigo.group(1)
            
            # Limpieza del nombre/etiqueta secundaria
            lineas = [l.strip() for l in texto.split("\n") if l.strip()]
            descripcion = lineas[0] if lineas else codigo

            resultado[codigo] = {
                "codigo": codigo,
                "estado": estado,
                "descripcion": descripcion,
                "color_badge": "🔴" if estado == "INACTIVA" else "🟢"
            }

    return resultado


# ---------------------------------------------------------
# EJEMPLO DE USO STANDALONE
# ---------------------------------------------------------
if __name__ == "__main__":
    # Sustituye con tu PHPSESSID actual obtenido desde las DevTools del navegador
    SESSION_ID = "tu_phpsessid_aqui"
    
    datos = extraer_estatus_epay(phpsessid=SESSION_ID)
    
    print(f"\nTotal máquinas detectadas: {len(datos)}\n")
    for codigo, info in datos.items():
        print(f"{info['color_badge']} {codigo} -> {info['estado']} ({info['descripcion']})")