import os
from datetime import datetime
import pandas as pd
import streamlit as st
from supabase import create_client, Client
from database import guardar_visita, init_db, obtener_visitas_df
from epay_scraper import extraer_estatus_epay

# Configuración Inicial
st.set_page_config(page_title="Vendu - Control de Operaciones", layout="wide")
init_db()  # Asegura que la BD exista

# ---------------------------------------------------------
# CACHÉ DE EPAY
# ---------------------------------------------------------
@st.cache_data(ttl=300)
def obtener_estatus_epay_cached(phpsessid):
    return extraer_estatus_epay(phpsessid)

# ---------------------------------------------------------
# CONFIGURACIÓN DE PÁGINA (PANTALLA TV 43")
# ---------------------------------------------------------
st.set_page_config(
    page_title='Tablero Logístico TV 43" - Control en Tiempo Real',
    page_icon="🚚",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ---------------------------------------------------------
# CONEXIÓN CON SUPABASE
# ---------------------------------------------------------
@st.cache_resource
def init_supabase() -> Client:
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
        return create_client(url, key)
    except Exception as e:
        st.error(
            f"⚠️ Error al conectar con Supabase. Revisa .streamlit/secrets.toml:"
            f" {e}"
        )
        st.stop()


supabase = init_supabase()

try:
    SUPERVISOR_PIN = st.secrets.get("SUPERVISOR_PIN", "1234")
except Exception:
    SUPERVISOR_PIN = "1234"

# ---------------------------------------------------------
# CONFIGURACIÓN DE ENTIDADES Y ESTADOS
# ---------------------------------------------------------
MOTORIZADOS_CONFIG = {
    "Eduard": {"code": "ED", "bg": "#2563eb", "color": "#ffffff"},
    "Freduard": {"code": "FR", "bg": "#7c3aed", "color": "#ffffff"},
    "Alejandro": {"code": "AL", "bg": "#059669", "color": "#ffffff"},
    "Gustavo": {"code": "GU", "bg": "#d97706", "color": "#ffffff"},
    "Sin Asignar": {"code": "--", "bg": "#334155", "color": "#94a3b8"},
}

MOTORIZADOS_DISPONIBLES = list(MOTORIZADOS_CONFIG.keys())

ESTADOS_CONFIG = {
    "PENDIENTE": {
        "label": "PENDIENTE",
        "icon": "⚪",
        "color": "#94a3b8",
        "bg": "#1e293b",
    },
    "EN_RUTA": {
        "label": "EN RUTA",
        "icon": "🟡",
        "color": "#f59e0b",
        "bg": "#78350f",
    },
    "COMPLETADO": {
        "label": "COMPLETADO",
        "icon": "🟢",
        "color": "#10b981",
        "bg": "#064e3b",
    },
}

DIAS_MAP = {
    0: "lunes",
    1: "martes",
    2: "miercoles",
    3: "jueves",
    4: "viernes",
    5: "sabado",
}

LLAVES_MUESTRA = {
    "KURIOS": "02",
    "CASHEA P9": "01",
    "CASHEA P18": "Maestra (M)",
    "CCS S1": "01/02",
    "CCS S2": "01/02",
    "FENIX": "02",
    "TIO AMMI 1": "01/02",
    "TIO AMMI 2": "01/02",
    "TU GRUERO": "0613",
    "UNION RADIO": "02",
}

LISTA_REAL_MAQUINAS = [
    ("Unimet PB", "Eduard", 1, 0, 1, 0, 0, 0, ""),
    ("Unimet LAB", "Eduard", 0, 1, 0, 1, 0, 0, ""),
    ("Unimet EM", "Eduard", 1, 0, 0, 0, 1, 0, ""),
    ("UCV ING", "Alejandro", 1, 0, 1, 0, 0, 0, ""),
    ("UCV COMP", "Alejandro", 0, 1, 0, 1, 0, 0, ""),
    ("UCAB CONVERT", "Freduard", 0, 0, 1, 1, 0, 0, ""),
    ("UCAB LAB", "Freduard", 0, 1, 0, 0, 1, 0, ""),
    ("UCAB P1", "Freduard", 1, 0, 0, 0, 0, 0, ""),
    ("UCAB MEZ", "Freduard", 0, 1, 0, 0, 0, 0, ""),
    ("UCAB M3", "Freduard", 0, 0, 1, 0, 0, 0, ""),
    ("USM", "Alejandro", 1, 0, 1, 0, 1, 0, ""),
    ("MONTAÑA", "Alejandro", 0, 0, 0, 1, 0, 0, ""),
    ("EURO S1", "Gustavo", 1, 0, 0, 1, 0, 0, ""),
    ("EURO S2", "Gustavo", 0, 1, 0, 0, 1, 0, ""),
    ("TAMACO", "Eduard", 0, 1, 0, 0, 0, 0, ""),
    ("TAMACA", "Eduard", 0, 1, 0, 0, 0, 0, ""),
    ("HUMBOLDT", "Alejandro", 1, 0, 0, 0, 0, 0, ""),
    ("GOLD DATA", "Gustavo", 0, 0, 1, 0, 0, 0, ""),
    ("PAGO DIRECTO", "Gustavo", 1, 0, 1, 0, 1, 0, ""),
    ("CUBITT", "Alejandro", 0, 1, 0, 1, 0, 0, ""),
    ("KURIOS", "Eduard", 0, 0, 0, 0, 1, 0, ""),
    ("CASHEA P9", "Freduard", 1, 0, 1, 0, 1, 0, ""),
    ("CASHEA P18", "Freduard", 1, 0, 1, 0, 1, 0, ""),
    ("DICAM", "Alejandro", 0, 1, 0, 0, 0, 0, ""),
    ("FISA", "Gustavo", 0, 0, 1, 0, 0, 0, ""),
    ("DOMESA", "Eduard", 1, 1, 1, 1, 1, 0, ""),
    ("TU GRUERO", "Alejandro", 0, 0, 0, 1, 0, 0, ""),
    ("UNION RADIO", "Gustavo", 1, 0, 0, 1, 0, 0, ""),
    ("FORUM P7", "Freduard", 0, 1, 0, 0, 1, 0, ""),
    ("FORUM P15", "Freduard", 0, 1, 0, 0, 1, 0, ""),
    ("BANGENTE", "Alejandro", 1, 0, 1, 0, 0, 0, ""),
    ("PROVINCIAL", "Gustavo", 1, 0, 0, 0, 0, 0, ""),
    ("TRANRED", "Eduard", 0, 0, 1, 0, 0, 0, ""),
    ("ROBIN", "Alejandro", 1, 0, 1, 0, 0, 0, ""),
    ("CALLCENTER DRCC", "Gustavo", 1, 0, 0, 0, 0, 0, ""),
    ("DUNCAN", "Eduard", 0, 0, 0, 1, 0, 0, ""),
    ("ANDROMEDA", "Alejandro", 1, 0, 0, 0, 1, 0, ""),
    ("PEGASO", "Alejandro", 0, 1, 0, 0, 0, 0, ""),
    ("TIO AMMI 1", "Freduard", 1, 0, 1, 0, 0, 0, ""),
    ("TIO AMMI 2", "Freduard", 0, 1, 0, 1, 0, 0, ""),
    ("RS1 RECEP", "Gustavo", 1, 0, 0, 1, 0, 0, ""),
    ("RS2 COMED", "Gustavo", 0, 1, 0, 0, 1, 0, ""),
    ("WECONNECT", "Eduard", 0, 0, 1, 0, 1, 0, ""),
    ("CEMENTERIO", "Alejandro", 1, 0, 0, 0, 0, 0, ""),
    ("HEBRAICA", "Freduard", 1, 0, 1, 0, 1, 0, ""),
    ("POLICLINICA P3", "Gustavo", 1, 0, 1, 0, 0, 0, ""),
    ("POLICLINICA P4", "Gustavo", 0, 1, 0, 1, 0, 0, ""),
    ("FLORESTA EM", "Eduard", 1, 0, 0, 1, 0, 0, ""),
    ("FLORESTA P3", "Eduard", 0, 1, 0, 0, 1, 0, ""),
    ("AVILA ADULT", "Alejandro", 1, 0, 1, 0, 0, 0, ""),
    ("AVILA PEDT", "Alejandro", 0, 1, 0, 1, 0, 0, ""),
    ("SANATRIX", "Freduard", 1, 0, 1, 0, 1, 0, ""),
    ("VENE CHACAO", "Gustavo", 1, 0, 0, 1, 0, 0, ""),
    ("VENE ALTAMIRA", "Gustavo", 0, 1, 0, 0, 1, 0, ""),
    ("VENE CANDELARIA", "Gustavo", 1, 0, 1, 0, 0, 0, ""),
    ("FLORIDA", "Eduard", 0, 0, 1, 0, 1, 0, ""),
    ("CCS S1", "Freduard", 1, 0, 0, 1, 0, 0, ""),
    ("CCS S2", "Freduard", 0, 1, 0, 0, 1, 0, ""),
    ("FENIX", "Alejandro", 0, 0, 1, 0, 1, 0, ""),
    ("OFICENTRO 1", "Gustavo", 1, 0, 1, 0, 0, 0, ""),
    ("OFICENTRO 2", "Gustavo", 0, 1, 0, 1, 0, 0, ""),
]


# ---------------------------------------------------------
# FUNCIONES DE BASE DE DATOS (SUPABASE)
# ---------------------------------------------------------
def init_db(force_reset=False):
    hoy_str = datetime.now().strftime("%Y-%m-%d")

    res = supabase.table("maquinas").select("id", count="exact").execute()
    total = res.count if res.count is not None else len(res.data)

    if total == 0 or force_reset:
        supabase.table("maquinas").delete().neq("id", 0).execute()

        payload = [
            {
                "nombre": m[0],
                "motorizado": m[1],
                "llave": LLAVES_MUESTRA.get(m[0], "N/A"),
                "lunes": m[2],
                "martes": m[3],
                "miercoles": m[4],
                "jueves": m[5],
                "viernes": m[6],
                "sabado": m[7],
                "observaciones": m[8],
                "estado": "PENDIENTE",
                "fecha_estado": hoy_str,
            }
            for m in LISTA_REAL_MAQUINAS
        ]

        supabase.table("maquinas").insert(payload).execute()


init_db()


def cargar_maquinas():
    hoy_str = datetime.now().strftime("%Y-%m-%d")

    supabase.table("maquinas").update(
        {"estado": "PENDIENTE", "fecha_estado": hoy_str}
    ).neq("fecha_estado", hoy_str).execute()

    res = supabase.table("maquinas").select("*").order("id").execute()

    if res.data:
        df = pd.DataFrame(res.data)

        if "llave" not in df.columns:
            df["llave"] = "N/A"
        else:
            df["llave"] = df["llave"].fillna("N/A").replace("", "N/A")

        dias_cols = ["lunes", "martes", "miercoles", "jueves", "viernes", "sabado"]
        for c in dias_cols:
            if c in df.columns:
                df[c] = df[c].astype(int)
        return df

    return pd.DataFrame()


def cambiar_estado_maquina(m_id, nuevo_estado):
    hoy_str = datetime.now().strftime("%Y-%m-%d")
    supabase.table("maquinas").update(
        {"estado": nuevo_estado, "fecha_estado": hoy_str}
    ).eq("id", m_id).execute()


def agregar_maquina(
    nombre, motorizado, llave, lunes, martes, miercoles, jueves, viernes, sabado
):
    hoy_str = datetime.now().strftime("%Y-%m-%d")
    payload = {
        "nombre": nombre,
        "motorizado": motorizado,
        "llave": llave.strip() if llave.strip() else "N/A",
        "lunes": int(lunes),
        "martes": int(martes),
        "miercoles": int(miercoles),
        "jueves": int(jueves),
        "viernes": int(viernes),
        "sabado": int(sabado),
        "observaciones": "",
        "estado": "PENDIENTE",
        "fecha_estado": hoy_str,
    }
    supabase.table("maquinas").insert(payload).execute()


def actualizar_maquina(
    m_id,
    nombre,
    motorizado,
    llave,
    lunes,
    martes,
    miercoles,
    jueves,
    viernes,
    sabado,
):
    payload = {
        "nombre": nombre,
        "motorizado": motorizado,
        "llave": llave.strip() if llave.strip() else "N/A",
        "lunes": int(lunes),
        "martes": int(martes),
        "miercoles": int(miercoles),
        "jueves": int(jueves),
        "viernes": int(viernes),
        "sabado": int(sabado),
    }
    supabase.table("maquinas").update(payload).eq("id", m_id).execute()


def eliminar_maquina(m_id):
    supabase.table("maquinas").delete().eq("id", m_id).execute()


# ---------------------------------------------------------
# ESTILOS CSS CORREGIDOS (COMPATIBLE CON STREAMLIT CLOUD)
# ---------------------------------------------------------
st.markdown(
    """
<style>
    /* 1. Desactivar captura de eventos en la barra superior pero mantener interactividad en hijos */
    header[data-testid="stHeader"] {
        background: transparent !important;
        z-index: 9999 !important;
        pointer-events: none !important;
    }

    /* Ocultar elementos decorativos secundarios */
    [data-testid="stDecoration"], 
    [data-testid="stStatusWidget"],
    #MainMenu, footer { 
        display: none !important; 
    }

    /* 2. Forzar visibilidad y clickeabilidad del botón flotante del Menú Sidebar */
    [data-testid="stSidebarCollapsedControl"],
    [data-testid="stSidebarCollapseButton"],
    button[aria-label="Open sidebar"],
    button[aria-label="Expand sidebar"],
    button[aria-label="Close sidebar"] {
        display: flex !important;
        visibility: visible !important;
        opacity: 1 !important;
        position: fixed !important;
        top: 12px !important;
        left: 12px !important;
        z-index: 1000000 !important;
        pointer-events: auto !important;
        background-color: #1e293b !important;
        border: 2px solid #38bdf8 !important;
        border-radius: 8px !important;
        padding: 6px !important;
        cursor: pointer !important;
        box-shadow: 0px 0px 12px rgba(56, 189, 248, 0.8) !important;
        transition: all 0.2s ease-in-out !important;
    }

    /* Estilo del icono SVG dentro del botón del menú */
    [data-testid="stSidebarCollapsedControl"] svg,
    [data-testid="stSidebarCollapseButton"] svg,
    button[aria-label="Open sidebar"] svg,
    button[aria-label="Close sidebar"] svg {
        fill: #38bdf8 !important;
        color: #38bdf8 !important;
        width: 22px !important;
        height: 22px !important;
    }

    /* Efecto al pasar el cursor sobre el botón desplegable */
    [data-testid="stSidebarCollapsedControl"]:hover,
    [data-testid="stSidebarCollapseButton"]:hover,
    button[aria-label="Open sidebar"]:hover {
        background-color: #38bdf8 !important;
        border-color: #ffffff !important;
    }

    [data-testid="stSidebarCollapsedControl"]:hover svg,
    [data-testid="stSidebarCollapseButton"]:hover svg,
    button[aria-label="Open sidebar"]:hover svg {
        fill: #0b1329 !important;
        color: #0b1329 !important;
    }

    /* Ocultar scrollbars por estética de TV */
    ::-webkit-scrollbar { display: none !important; width: 0px !important; }
    * { scrollbar-width: none !important; }

    /* Estilos globales para pantalla oscura en TV 43" */
    html, body, .stApp { 
        background-color: #0b1329 !important; 
        color: #f8fafc !important; 
        margin: 0 !important; 
        padding: 0 !important; 
    }
    
    .block-container { 
        padding-top: 2.8rem !important; 
        padding-bottom: 0.2rem !important;
        padding-left: 0.5rem !important;
        padding-right: 0.5rem !important;
        max-width: 100% !important; 
    }

    /* Badges */
    .moto-badge { 
        display: inline-block; 
        padding: 3px 8px; 
        border-radius: 5px; 
        font-weight: 900; 
        font-size: clamp(0.8rem, 0.88vw, 0.98rem); 
        text-align: center; 
    }

    .key-badge {
        display: inline-block; padding: 2px 6px; border-radius: 4px; font-weight: 800; 
        font-size: clamp(0.72rem, 0.8vw, 0.88rem);
        background-color: #1e293b; color: #38bdf8; border: 1px solid #334155; margin-left: 4px; vertical-align: middle;
    }
    .key-badge-na {
        display: inline-block; padding: 2px 5px; border-radius: 4px; font-weight: 700; 
        font-size: clamp(0.68rem, 0.75vw, 0.82rem);
        background-color: #111c30; color: #64748b; border: 1px solid #1e293b; margin-left: 4px; vertical-align: middle;
    }

    .status-badge { 
        display: inline-block; padding: 2px 6px; border-radius: 4px; font-weight: 800; 
        font-size: clamp(0.72rem, 0.8vw, 0.88rem); text-align: center; margin-left: 4px; 
    }
    .status-PENDIENTE { background-color: #334155; color: #cbd5e1; }
    .status-EN_RUTA { background-color: #854d0e; color: #fef08a; }
    .status-COMPLETADO { background-color: #065f46; color: #a7f3d0; }

    /* Resaltado Día Actual */
    .today-col-header { background-color: #1e3a8a !important; color: #38bdf8 !important; border-bottom: 2px solid #38bdf8 !important; }

    /* Rejilla y Tablas */
    .tv-grid { display: flex; flex-direction: row; gap: 10px; width: 100%; }
    .tv-column { flex: 1; background-color: #111c30; border-radius: 8px; border: 1px solid #1e293b; overflow: hidden; }
    .tv-table { width: 100%; border-collapse: collapse; font-family: system-ui, -apple-system, sans-serif; }
    
    .tv-table th { 
        background-color: #0b1329; color: #94a3b8; 
        font-size: clamp(0.85rem, 0.92vw, 1.05rem); 
        font-weight: 800; padding: clamp(6px, 0.7vh, 10px) 0.5rem; 
        border-bottom: 2px solid #1e293b; text-align: left; 
    }
    .tv-table th.center-header { text-align: center; }
    
    .tv-table td { 
        padding: clamp(4px, 0.55vh, 8px) 0.5rem !important; 
        border-bottom: 1px solid #172338; 
        vertical-align: middle; white-space: nowrap; line-height: 1.25; 
    }
    
    .location-name { 
        font-size: clamp(0.9rem, 0.98vw, 1.12rem); 
        font-weight: 800; color: #ffffff !important; 
    }
    .tv-table tr:nth-child(even) { background-color: #0d1627; }

    .day-check { color: #38bdf8; font-weight: 900; font-size: clamp(0.95rem, 1.05vw, 1.2rem); }
    .day-check-sat { color: #c084fc; font-weight: 900; font-size: clamp(0.95rem, 1.05vw, 1.2rem); }
    .day-off { color: #1e293b; font-size: 0.85rem; }

    .row-COMPLETADO { opacity: 0.5; }
</style>
""",
    unsafe_allow_html=True,
)


# ---------------------------------------------------------
# RENDERING DE TABLERO (TV 43" - DIRECTO A TABLA)
# ---------------------------------------------------------
@st.fragment(run_every=10)
def renderizar_tablero_vertical(estatus_epay=None):
    if estatus_epay is None:
        estatus_epay = {}
        
    dt_now = datetime.now()
    dia_num = dt_now.weekday()

    df_maquinas = cargar_maquinas()

    if df_maquinas.empty:
        st.warning("No hay máquinas registradas en la base de datos de Supabase.")
        return

    def get_cell(active, is_sat=False):
        if active:
            cls = "day-check-sat" if is_sat else "day-check"
            return f'<span class="{cls}">✓</span>'
        return '<span class="day-off">-</span>'

    def get_moto_badge(motorizado_nombre):
        cfg = MOTORIZADOS_CONFIG.get(
            motorizado_nombre, MOTORIZADOS_CONFIG["Sin Asignar"]
        )
        return (
            f'<span class="moto-badge" style="background-color: {cfg["bg"]};'
            f' color: {cfg["color"]};">{cfg["code"]}</span>'
        )

    def get_status_badge(estado):
        est = ESTADOS_CONFIG.get(estado, ESTADOS_CONFIG["PENDIENTE"])
        return f'<span class="status-badge status-{estado}">{est["icon"]}</span>'

    def get_key_badge(llave_val):
        if llave_val and llave_val != "N/A":
            return f'<span class="key-badge">🔑 {llave_val}</span>'
        return '<span class="key-badge-na">🔑 N/A</span>'

    mitad = (len(df_maquinas) + 1) // 2
    df_col1 = df_maquinas.iloc[:mitad]
    df_col2 = df_maquinas.iloc[mitad:]

    h_l = "today-col-header" if dia_num == 0 else ""
    h_m = "today-col-header" if dia_num == 1 else ""
    h_x = "today-col-header" if dia_num == 2 else ""
    h_j = "today-col-header" if dia_num == 3 else ""
    h_v = "today-col-header" if dia_num == 4 else ""
    h_s = "today-col-header" if dia_num == 5 else ""

    def construir_tabla_html(df_sub):
        rows_list = []
        for _, m in df_sub.iterrows():
            badge_moto = get_moto_badge(m["motorizado"])
            badge_estado = get_status_badge(m["estado"])
            badge_llave = get_key_badge(m.get("llave", "N/A"))
            c_l = get_cell(m["lunes"])
            c_m = get_cell(m["martes"])
            c_x = get_cell(m["miercoles"])
            c_j = get_cell(m["jueves"])
            c_v = get_cell(m["viernes"])
            c_s = get_cell(m["sabado"], is_sat=True)

            row_class = f"row-{m['estado']}" if m["estado"] == "COMPLETADO" else ""

            rows_list.append(
                f'<tr class="{row_class}">'
                f'<td class="location-name">{m["nombre"]} {badge_llave}'
                f' {badge_estado}</td>'
                f'<td style="text-align: center;">{badge_moto}</td>'
                f'<td style="text-align: center;">{c_l}</td>'
                f'<td style="text-align: center;">{c_m}</td>'
                f'<td style="text-align: center;">{c_x}</td>'
                f'<td style="text-align: center;">{c_j}</td>'
                f'<td style="text-align: center;">{c_v}</td>'
                f'<td style="text-align: center;">{c_s}</td>'
                "</tr>"
            )

        html_rows = "".join(rows_list)
        return (
            f'<div class="tv-column"><table class="tv-table"><thead><tr>'
            f'<th style="width: 44%;">UBICACIÓN</th>'
            f'<th class="center-header" style="width: 14%;">RESP.</th>'
            f'<th class="center-header {h_l}" style="width: 7%;">L</th>'
            f'<th class="center-header {h_m}" style="width: 7%;">M</th>'
            f'<th class="center-header {h_x}" style="width: 7%;">X</th>'
            f'<th class="center-header {h_j}" style="width: 7%;">J</th>'
            f'<th class="center-header {h_v}" style="width: 7%;">V</th>'
            f'<th class="center-header {h_s}" style="width: 7%;">S</th>'
            f"</tr></thead><tbody>{html_rows}</tbody></table></div>"
        )

    tabla1_html = construir_tabla_html(df_col1)
    tabla2_html = construir_tabla_html(df_col2)

    st.markdown(
        f'<div class="tv-grid">{tabla1_html}{tabla2_html}</div>',
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------
# NAVEGACIÓN Y PANELES
# ---------------------------------------------------------
st.sidebar.title("🎛️ NAVEGACIÓN")
modo = st.sidebar.radio(
    "Seleccionar Vista:",
    ["📱 Tablero TV (En Vivo)", "⚡ Control de Ruta Hoy", "⚙️ Panel de Gestión", "☕ Máquinas de Café", "🛵 App Motorizados", "📊 Dashboard Semanal"],
)

if modo == "📺 Tablero TV (En Vivo)":
    # 1. Obtener la telemetría de ePay en tiempo real
    phpsessid = st.secrets.get("EPAY_PHPSESSID", "tu_session_id_aqui")
    estatus_epay = obtener_estatus_epay_cached(phpsessid)

    # 2. Renderizar el tablero pasándole los datos de ePay
    renderizar_tablero_vertical(estatus_epay)

elif modo == "📺 Tablero Snacky":
    st.title("📺 Tablero Logístico Snacky")

    # Obtenemos Cookie de sesión
    phpsessid = st.secrets.get("EPAY_PHPSESSID", "tu_session_id_aqui")
    estatus_epay = obtener_estatus_epay_cached(phpsessid)

    st.info("🟢 = Máquina Activa en ePay | 🔴 = Máquina Inactiva / Offline")

    # Lista de máquinas de prueba
    maquinas_snacky = [
        {"codigo_epay": "V07-CASH09", "nombre": "Cashea Piso 9", "llave": "01"},
        {"codigo_epay": "V01-UCLABS", "nombre": "UCAB Laboratorios", "llave": "02"},
        {"codigo_epay": "V03-UCAP1", "nombre": "UCAB Cinc. Piso 1", "llave": "03"},
        {"codigo_epay": "V25-UCV", "nombre": "UCV Central", "llave": "04"},
    ]

    for m in maquinas_snacky:
        code = m["codigo_epay"]
        info = estatus_epay.get(code, {})
        badge = info.get("color_badge", "⚪")
        estado_txt = info.get("estado", "SIN DATOS")

        st.markdown(f"### {badge} **{m['nombre']}** (`{code}`)")
        st.caption(f"Estado Telemetría: **{estado_txt}** | Llave: **{m['llave']}**")
        st.divider()

elif modo == "☕ Máquinas de Café":
    st.title("☕ Gestión de Máquinas de Café")

    # ---------------------------------------------------------
    # 1. CONFIGURACIÓN DEL MOTORIZADO ÚNICO (JUAN)
    # ---------------------------------------------------------
    MOTORIZADO_CAFE = {
        "Juan": {"code": "JU", "bg": "#ec4899", "color": "#ffffff"}
    }

    # Dict por defecto para fallback de estados si no existe ESTADOS_CONFIG global
    ESTADOS_DEFAULT = {
        "PENDIENTE": {"icon": "⏳", "label": "Pendiente"},
        "EN_RUTA": {"icon": "🛵", "label": "En Ruta"},
        "COMPLETADO": {"icon": "✅", "label": "Completado"},
    }
    config_estados = globals().get("ESTADOS_CONFIG", ESTADOS_DEFAULT)

    # ---------------------------------------------------------
    # 2. DATOS EXTRAÍDOS DEL CRONOGRAMA MANUSCRITO
    # ---------------------------------------------------------
    DATOS_MAQUINAS_CAFE = [
        {
            "nombre": "Clínicas Caracas",
            "direccion": "San Bernardino, Caracas",
            "llave": "N/A",
            "horarios": {
                "lunes": "",
                "martes": "9:30 am",
                "miercoles": "",
                "jueves": "9:30 am",
                "viernes": "",
                "sabado": "9:30 am",
            },
            "estado": "PENDIENTE",
        },
        {
            "nombre": "Cashea P17",
            "direccion": "Torre HP, Piso 9, Chacao",
            "llave": "01",
            "horarios": {
                "lunes": "",
                "martes": "9:30 am",
                "miercoles": "9:30 am",
                "jueves": "",
                "viernes": "9:30 am",
                "sabado": "",
            },
            "estado": "PENDIENTE",
        },
        {
            "nombre": "Cashea P18",
            "direccion": "Torre HP, Piso 18, Chacao",
            "llave": "Maestra (M)",
            "horarios": {
                "lunes": "9:30 am",
                "martes": "",
                "miercoles": "9:30 am",
                "jueves": "",
                "viernes": "9:30 am",
                "sabado": "",
            },
            "estado": "PENDIENTE",
        },
        {
            "nombre": "CMDLT",
            "direccion": "Centro Médico Docente La Trinidad",
            "llave": "N/A",
            "horarios": {
                "lunes": "7:00 am",
                "martes": "",
                "miercoles": "7:00 am",
                "jueves": "",
                "viernes": "7:00 am",
                "sabado": "2:00 pm",
            },
            "estado": "PENDIENTE",
        },
        {
            "nombre": "UR (Unión Radio)",
            "direccion": "Av. La Estancia, La Castellana",
            "llave": "02",
            "horarios": {
                "lunes": "10:30 am",
                "martes": "",
                "miercoles": "10:30 am",
                "jueves": "",
                "viernes": "10:30 am",
                "sabado": "",
            },
            "estado": "PENDIENTE",
        },
        {
            "nombre": "Sanatrix",
            "direccion": "Clínica Sanatrix, Chacao",
            "llave": "N/A",
            "horarios": {
                "lunes": "",
                "martes": "1:30 pm",
                "miercoles": "",
                "jueves": "1:30 pm",
                "viernes": "",
                "sabado": "1:30 pm",
            },
            "estado": "PENDIENTE",
        },
        {
            "nombre": "Bangente",
            "direccion": "Av. Francisco de Miranda",
            "llave": "N/A",
            "horarios": {
                "lunes": "8:30 am",
                "martes": "",
                "miercoles": "",
                "jueves": "8:30 am",
                "viernes": "8:30 am",
                "sabado": "",
            },
            "estado": "PENDIENTE",
        },
        {
            "nombre": "Ávila Recep / D",
            "direccion": "Clínica Ávila, Altamira",
            "llave": "N/A",
            "horarios": {
                "lunes": "1:30 pm",
                "martes": "",
                "miercoles": "",
                "jueves": "1:30 pm",
                "viernes": "1:30 pm",
                "sabado": "",
            },
            "estado": "PENDIENTE",
        },
        {
            "nombre": "Fenix",
            "direccion": "Edif. Fenix",
            "llave": "02",
            "horarios": {
                "lunes": "12:30 pm",
                "martes": "10:30 am",
                "miercoles": "",
                "jueves": "10:30 am",
                "viernes": "12:30 pm",
                "sabado": "10:30 am",
            },
            "estado": "PENDIENTE",
        },
        {
            "nombre": "Florida",
            "direccion": "Urb. La Florida",
            "llave": "N/A",
            "horarios": {
                "lunes": "",
                "martes": "7:30 am",
                "miercoles": "7:30 am",
                "jueves": "7:30 am",
                "viernes": "",
                "sabado": "",
            },
            "estado": "PENDIENTE",
        },
        {
            "nombre": "Weconnect",
            "direccion": "Sede Weconnect",
            "llave": "N/A",
            "horarios": {
                "lunes": "",
                "martes": "8:30 am",
                "miercoles": "",
                "jueves": "8:30 am",
                "viernes": "",
                "sabado": "",
            },
            "estado": "PENDIENTE",
        },
        {
            "nombre": "Kurios",
            "direccion": "Sede Kurios",
            "llave": "02",
            "horarios": {
                "lunes": "",
                "martes": "12:30 pm",
                "miercoles": "",
                "jueves": "12:30 pm",
                "viernes": "",
                "sabado": "12:30 pm",
            },
            "estado": "PENDIENTE",
        },
    ]

    # Construcción de DataFrame para el dashboard
    rows_cafe = []
    for item in DATOS_MAQUINAS_CAFE:
        h = item["horarios"]
        rows_cafe.append(
            {
                "nombre": item["nombre"],
                "direccion": item["direccion"],
                "llave": item["llave"],
                "lunes": 1 if h["lunes"] else 0,
                "martes": 1 if h["martes"] else 0,
                "miercoles": 1 if h["miercoles"] else 0,
                "jueves": 1 if h["jueves"] else 0,
                "viernes": 1 if h["viernes"] else 0,
                "sabado": 1 if h["sabado"] else 0,
                "h_lunes": h["lunes"],
                "h_martes": h["martes"],
                "h_miercoles": h["miercoles"],
                "h_jueves": h["jueves"],
                "h_viernes": h["viernes"],
                "h_sabado": h["sabado"],
                "estado": item["estado"],
            }
        )

    df_cafe = pd.DataFrame(rows_cafe)

    # ---------------------------------------------------------
    # 3. PESTAÑAS DEL APARTADO
    # ---------------------------------------------------------
    tab_tablero, tab_cronograma, tab_direcciones = st.tabs(
        ["📺 Tablero TV (Juan)", "📅 Cronograma Fijo", "📍 Direcciones y Puntos"]
    )

    # ---------------------------------------------------------
    # TAB 1: TABLERO TV (MISMA ESTRUCTURA DE SNACKY)
    # ---------------------------------------------------------
    with tab_tablero:
        dt_now = datetime.now()
        dia_num = dt_now.weekday()

        def get_cell_cafe(active, is_sat=False):
            if active:
                cls = "day-check-sat" if is_sat else "day-check"
                return f'<span class="{cls}">✓</span>'
            return '<span class="day-off">-</span>'

        badge_juan = f'<span class="moto-badge" style="background-color: {MOTORIZADO_CAFE["Juan"]["bg"]}; color: {MOTORIZADO_CAFE["Juan"]["color"]};">{MOTORIZADO_CAFE["Juan"]["code"]}</span>'

        mitad = (len(df_cafe) + 1) // 2
        col1_cafe = df_cafe.iloc[:mitad]
        col2_cafe = df_cafe.iloc[mitad:]

        h_l = "today-col-header" if dia_num == 0 else ""
        h_m = "today-col-header" if dia_num == 1 else ""
        h_x = "today-col-header" if dia_num == 2 else ""
        h_j = "today-col-header" if dia_num == 3 else ""
        h_v = "today-col-header" if dia_num == 4 else ""
        h_s = "today-col-header" if dia_num == 5 else ""

        def render_tabla_cafe(df_sub):
            rows_list = []
            for _, m in df_sub.iterrows():
                est = config_estados.get(
                    m["estado"], config_estados["PENDIENTE"]
                )
                badge_estado = f'<span class="status-badge status-{m["estado"]}">{est["icon"]}</span>'
                badge_llave = (
                    f'<span class="key-badge">🔑 {m["llave"]}</span>'
                    if m["llave"] != "N/A"
                    else '<span class="key-badge-na">🔑 N/A</span>'
                )

                c_l = get_cell_cafe(m["lunes"])
                c_m = get_cell_cafe(m["martes"])
                c_x = get_cell_cafe(m["miercoles"])
                c_j = get_cell_cafe(m["jueves"])
                c_v = get_cell_cafe(m["viernes"])
                c_s = get_cell_cafe(m["sabado"], is_sat=True)

                row_class = (
                    f"row-{m['estado']}" if m["estado"] == "COMPLETADO" else ""
                )

                rows_list.append(
                    f'<tr class="{row_class}">'
                    f'<td class="location-name">{m["nombre"]} {badge_llave} {badge_estado}</td>'
                    f'<td style="text-align: center;">{badge_juan}</td>'
                    f'<td style="text-align: center;">{c_l}</td>'
                    f'<td style="text-align: center;">{c_m}</td>'
                    f'<td style="text-align: center;">{c_x}</td>'
                    f'<td style="text-align: center;">{c_j}</td>'
                    f'<td style="text-align: center;">{c_v}</td>'
                    f'<td style="text-align: center;">{c_s}</td>'
                    "</tr>"
                )

            html_rows = "".join(rows_list)
            return (
                f'<div class="tv-column"><table class="tv-table"><thead><tr>'
                f'<th style="width: 44%;">PUNTO DE CAFÉ</th>'
                f'<th class="center-header" style="width: 14%;">RESP.</th>'
                f'<th class="center-header {h_l}" style="width: 7%;">L</th>'
                f'<th class="center-header {h_m}" style="width: 7%;">M</th>'
                f'<th class="center-header {h_x}" style="width: 7%;">X</th>'
                f'<th class="center-header {h_j}" style="width: 7%;">J</th>'
                f'<th class="center-header {h_v}" style="width: 7%;">V</th>'
                f'<th class="center-header {h_s}" style="width: 7%;">S</th>'
                f"</tr></thead><tbody>{html_rows}</tbody></table></div>"
            )

        t1_html = render_tabla_cafe(col1_cafe)
        t2_html = render_tabla_cafe(col2_cafe)

        st.markdown(
            f'<div class="tv-grid">{t1_html}{t2_html}</div>',
            unsafe_allow_html=True,
        )

    # ---------------------------------------------------------
    # TAB 2: CRONOGRAMA FIJO
    # ---------------------------------------------------------
    with tab_cronograma:
        st.subheader("📅 Cronograma Semanal Fijo de Café")
        st.caption("Horarios exactos asignados al motorizado **Juan (JU)**")

        dias_semana = [
            ("Lunes", "lunes", "h_lunes"),
            ("Martes", "martes", "h_martes"),
            ("Miércoles", "miercoles", "h_miercoles"),
            ("Jueves", "jueves", "h_jueves"),
            ("Viernes", "viernes", "h_viernes"),
            ("Sábado", "sabado", "h_sabado"),
        ]

        cols_dias = st.columns(6)

        for idx, (nombre_dia, col_flag, col_hora) in enumerate(dias_semana):
            with cols_dias[idx]:
                st.markdown(f"### {nombre_dia}")
                puntos_dia = df_cafe[df_cafe[col_flag] == 1]

                if puntos_dia.empty:
                    st.info("Sin visitas")
                else:
                    for _, p in puntos_dia.iterrows():
                        llave_tag = (
                            f"`🔑 {p['llave']}`" if p["llave"] != "N/A" else ""
                        )
                        st.markdown(
                            f"⏰ **{p[col_hora]}**\n\n**{p['nombre']}**\n{llave_tag}"
                        )
                        st.divider()

    # ---------------------------------------------------------
    # TAB 3: DIRECCIONES Y PUNTOS
    # ---------------------------------------------------------
    with tab_direcciones:
        st.subheader("📍 Directorio Ubicaciones y Direcciones de Café")

        busqueda_dir = st.text_input(
            "🔍 Buscar por punto o dirección:",
            placeholder="Ej: Cashea, Clínica, Unión Radio...",
        )

        df_dir_display = df_cafe[["nombre", "direccion", "llave"]].copy()

        if busqueda_dir:
            df_dir_display = df_dir_display[
                df_dir_display["nombre"].str.contains(
                    busqueda_dir, case=False, na=False
                )
                | df_dir_display["direccion"].str.contains(
                    busqueda_dir, case=False, na=False
                )
            ]

        st.dataframe(
            df_dir_display.rename(
                columns={
                    "nombre": "Punto de Café",
                    "direccion": "Dirección Exacta",
                    "llave": "Llave de Acceso",
                }
            ),
            use_container_width=True,
            hide_index=True,
        )

elif modo == "⚡ Control de Ruta Hoy":
    st.title("⚡ Control de Avance de Ruta (Hoy)")
    st.markdown("Actualice el estado operacional de cada punto según la ruta del día:")

    df_maquinas = cargar_maquinas()

    if df_maquinas.empty:
        st.info("No existen máquinas registradas.")
    else:
        dia_num = datetime.now().weekday()
        nombre_dia_hoy = DIAS_MAP.get(dia_num, "lunes")

        col_f1, col_f2 = st.columns([1, 2])
        filt_moto = col_f1.selectbox(
            "Filtrar por Motorizado:", ["Todos"] + MOTORIZADOS_DISPONIBLES
        )
        busqueda_ruta = col_f2.text_input(
            "🔍 Buscar ubicación o llave:",
            placeholder="Ej: Unimet, 01/02, Cashea...",
        )

        df_filtrado = df_maquinas[df_maquinas[nombre_dia_hoy] == 1]

        if filt_moto != "Todos":
            df_filtrado = df_filtrado[df_filtrado["motorizado"] == filt_moto]

        if busqueda_ruta:
            df_filtrado = df_filtrado[
                df_filtrado["nombre"].str.contains(
                    busqueda_ruta, case=False, na=False
                )
                | df_filtrado["llave"].str.contains(
                    busqueda_ruta, case=False, na=False
                )
            ]

        st.subheader(
            f"Puntos asignados para hoy ({nombre_dia_hoy.upper()}):"
            f" {len(df_filtrado)}"
        )

        for index, m in df_filtrado.iterrows():
            col_name, col_status, col_btn1, col_btn2, col_btn3 = st.columns(
                [3, 2, 1.5, 1.5, 1.5]
            )

            llave_str = f"`🔑 {m['llave']}`" if m["llave"] != "N/A" else ""
            col_name.markdown(f"**{m['nombre']}** {llave_str} (`{m['motorizado']}`)")

            est_actual = m["estado"]
            col_status.markdown(
                f"{ESTADOS_CONFIG[est_actual]['icon']} **{ESTADOS_CONFIG[est_actual]['label']}**"
            )

            if col_btn1.button("⚪ Pendiente", key=f"p_{m['id']}"):
                cambiar_estado_maquina(m["id"], "PENDIENTE")
                st.rerun()

            if col_btn2.button("🟡 En Ruta", key=f"r_{m['id']}"):
                cambiar_estado_maquina(m["id"], "EN_RUTA")
                st.rerun()

            if col_btn3.button("🟢 Completado", key=f"c_{m['id']}"):
                cambiar_estado_maquina(m["id"], "COMPLETADO")
                st.rerun()

            st.divider()

elif modo == "⚙️ Panel de Gestión":
    st.title("⚙️ Panel de Gestión y Supervisión")
    st.markdown("---")

    pin_ingresado = st.sidebar.text_input("Clave Supervisor:", type="password")

    if pin_ingresado != SUPERVISOR_PIN:
        st.warning("🔒 Ingrese la clave de supervisor correcta para editar.")
    else:
        st.success("🔓 Acceso concedido.")

        if st.sidebar.button("🔄 Recargar Ubicaciones Iniciales"):
            init_db(force_reset=True)
            st.sidebar.success(
                "¡Base de datos restablecida en Supabase con éxito!"
            )
            st.rerun()

        col_form, col_tabla = st.columns([1, 2])

        with col_form:
            st.subheader("➕ Agregar Nueva Ubicación")
            with st.form("form_agregar", clear_on_submit=True):
                nombre_nuevo = st.text_input("Nombre de Ubicación:")
                moto_nuevo = st.selectbox(
                    "Motorizado Asignado:", MOTORIZADOS_DISPONIBLES, index=0
                )
                llave_nueva = st.text_input(
                    "Tipo / Número de Llave:",
                    value="N/A",
                    placeholder="Ej: 01, 02, Maestra (M), 01/02...",
                )

                st.write("**Días de Recarga:**")
                c_l, c_m, c_x, c_j, c_v, c_s = st.columns(6)
                l_val = c_l.checkbox("L", value=True)
                m_val = c_m.checkbox("M", value=False)
                x_val = c_x.checkbox("X", value=False)
                j_val = c_j.checkbox("J", value=False)
                v_val = c_v.checkbox("V", value=False)
                s_val = c_s.checkbox("S", value=False)

                btn_guardar = st.form_submit_button("💾 Guardar")

                if btn_guardar and nombre_nuevo.strip():
                    agregar_maquina(
                        nombre_nuevo,
                        moto_nuevo,
                        llave_nueva,
                        l_val,
                        m_val,
                        x_val,
                        j_val,
                        v_val,
                        s_val,
                    )
                    st.success("Ubicación agregada en Supabase.")
                    st.rerun()

        with col_tabla:
            st.subheader("📋 Modificar / Eliminar Ubicaciones")

            busqueda_sup = st.text_input(
                "🔍 Buscador Rápido de Máquinas:",
                placeholder="Escriba el nombre, motorizado o llave...",
            )

            df = cargar_maquinas()

            if busqueda_sup and not df.empty:
                df = df[
                    df["nombre"].str.contains(busqueda_sup, case=False, na=False)
                    | df["motorizado"].str.contains(busqueda_sup, case=False, na=False)
                    | df["llave"].str.contains(busqueda_sup, case=False, na=False)
                ]

            st.caption(f"Mostrando {len(df)} máquina(s)")

            for index, row in df.iterrows():
                cfg = MOTORIZADOS_CONFIG.get(
                    row["motorizado"], MOTORIZADOS_CONFIG["Sin Asignar"]
                )
                llave_tag = f" | 🔑 {row['llave']}" if row["llave"] != "N/A" else ""

                with st.expander(
                    f"📌 {row['nombre']}{llave_tag} | [{cfg['code']}] {row['motorizado']}"
                ):
                    with st.form(f"form_edit_{row['id']}"):
                        e_nombre = st.text_input("Ubicación:", value=row["nombre"])
                        e_llave = st.text_input(
                            "Tipo / N° de Llave:",
                            value=row["llave"],
                            key=f"llave_{row['id']}",
                        )

                        idx_moto = (
                            MOTORIZADOS_DISPONIBLES.index(row["motorizado"])
                            if row["motorizado"] in MOTORIZADOS_DISPONIBLES
                            else 4
                        )
                        e_moto = st.selectbox(
                            "Motorizado:",
                            MOTORIZADOS_DISPONIBLES,
                            index=idx_moto,
                            key=f"moto_{row['id']}",
                        )

                        st.write("**Días Activos:**")
                        d1, d2, d3, d4, d5, d6 = st.columns(6)
                        e_l = d1.checkbox(
                            "L", value=bool(row["lunes"]), key=f"l_{row['id']}"
                        )
                        e_m = d2.checkbox(
                            "M", value=bool(row["martes"]), key=f"m_{row['id']}"
                        )
                        e_x = d3.checkbox(
                            "X", value=bool(row["miercoles"]), key=f"x_{row['id']}"
                        )
                        e_j = d4.checkbox(
                            "J", value=bool(row["jueves"]), key=f"j_{row['id']}"
                        )
                        e_v = d5.checkbox(
                            "V", value=bool(row["viernes"]), key=f"v_{row['id']}"
                        )
                        e_s = d6.checkbox(
                            "S", value=bool(row["sabado"]), key=f"s_{row['id']}"
                        )

                        b1, b2 = st.columns(2)
                        if b1.form_submit_button("💾 Actualizar"):
                            actualizar_maquina(
                                row["id"],
                                e_nombre,
                                e_moto,
                                e_llave,
                                e_l,
                                e_m,
                                e_x,
                                e_j,
                                e_v,
                                e_s,
                            )
                            st.success("¡Máquina actualizada!")
                            st.rerun()

                        if b2.form_submit_button("🗑️ Eliminar"):
                            eliminar_maquina(row["id"])
                            st.rerun()