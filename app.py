import os
from datetime import datetime
import pandas as pd
import streamlit as st
from supabase import create_client, Client

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
# ESTILOS CSS (POSICIONAMIENTO GARANTIZADO DE FLECHA + TAMAÑO OPTIMIZADO)
# ---------------------------------------------------------
st.markdown(
    """
<style>
    /* 1. Transparencia del contenedor superior para dar paso al botón flotante */
    header[data-testid="stHeader"] {
        background: transparent !important;
        height: 0px !important;
        overflow: visible !important;
        z-index: 99999 !important;
    }

    /* Ocultar únicamente el menú de opciones desplegable y decoraciones */
    [data-testid="stToolbar"], 
    [data-testid="stDecoration"], 
    [data-testid="stStatusWidget"],
    #MainMenu, footer { 
        display: none !important; 
    }

    /* 2. Forzar posición fija y alta visibilidad del botón desplegable del Menú Lateral */
    [data-testid="stSidebarCollapsedControl"] {
        display: flex !important;
        visibility: visible !important;
        position: fixed !important;
        top: 8px !important;
        left: 8px !important;
        z-index: 100000 !important;
        background-color: #1e293b !important;
        border: 2px solid #38bdf8 !important;
        border-radius: 8px !important;
        padding: 2px !important;
        box-shadow: 0px 0px 8px rgba(56, 189, 248, 0.4) !important;
    }

    [data-testid="stSidebarCollapsedControl"] button {
        color: #38bdf8 !important;
    }

    /* Ocultar scrollbars */
    ::-webkit-scrollbar { display: none !important; width: 0px !important; }
    * { scrollbar-width: none !important; }

    /* Estilos globales */
    html, body, .stApp { 
        background-color: #0b1329 !important; 
        color: #f8fafc !important; 
        margin: 0 !important; 
        padding: 0 !important; 
    }
    
    /* Espaciado para evitar que el botón del sidebar solape el texto */
    .block-container { 
        padding-top: 2.4rem !important; 
        padding-bottom: 0.2rem !important;
        padding-left: 0.4rem !important;
        padding-right: 0.4rem !important;
        max-width: 100% !important; 
    }

    /* Badges con tipografía aumentada */
    .moto-badge { 
        display: inline-block; 
        padding: 2px 7px; 
        border-radius: 4px; 
        font-weight: 900; 
        font-size: clamp(0.75rem, 0.82vw, 0.92rem); 
        text-align: center; 
    }

    .key-badge {
        display: inline-block; padding: 2px 5px; border-radius: 4px; font-weight: 800; 
        font-size: clamp(0.68rem, 0.75vw, 0.82rem);
        background-color: #1e293b; color: #38bdf8; border: 1px solid #334155; margin-left: 4px; vertical-align: middle;
    }
    .key-badge-na {
        display: inline-block; padding: 2px 4px; border-radius: 4px; font-weight: 700; 
        font-size: clamp(0.65rem, 0.7vw, 0.78rem);
        background-color: #111c30; color: #64748b; border: 1px solid #1e293b; margin-left: 4px; vertical-align: middle;
    }

    .status-badge { 
        display: inline-block; padding: 2px 5px; border-radius: 4px; font-weight: 800; 
        font-size: clamp(0.68rem, 0.75vw, 0.82rem); text-align: center; margin-left: 4px; 
    }
    .status-PENDIENTE { background-color: #334155; color: #cbd5e1; }
    .status-EN_RUTA { background-color: #854d0e; color: #fef08a; }
    .status-COMPLETADO { background-color: #065f46; color: #a7f3d0; }

    /* Resaltado Día Actual */
    .today-col-header { background-color: #1e3a8a !important; color: #38bdf8 !important; border-bottom: 2px solid #38bdf8 !important; }

    /* Rejilla y Tablas Optimizadas (Mayor aprovechamiento vertical) */
    .tv-grid { display: flex; flex-direction: row; gap: 8px; width: 100%; }
    .tv-column { flex: 1; background-color: #111c30; border-radius: 8px; border: 1px solid #1e293b; overflow: hidden; }
    .tv-table { width: 100%; border-collapse: collapse; font-family: system-ui, -apple-system, sans-serif; }
    
    .tv-table th { 
        background-color: #0b1329; color: #94a3b8; 
        font-size: clamp(0.8rem, 0.88vw, 0.98rem); 
        font-weight: 800; padding: clamp(4px, 0.5vh, 8px) 0.4rem; 
        border-bottom: 2px solid #1e293b; text-align: left; 
    }
    .tv-table th.center-header { text-align: center; }
    
    .tv-table td { 
        padding: clamp(3px, 0.42vh, 6px) 0.4rem !important; 
        border-bottom: 1px solid #172338; 
        vertical-align: middle; white-space: nowrap; line-height: 1.2; 
    }
    
    .location-name { 
        font-size: clamp(0.85rem, 0.92vw, 1.05rem); 
        font-weight: 800; color: #ffffff !important; 
    }
    .tv-table tr:nth-child(even) { background-color: #0d1627; }

    .day-check { color: #38bdf8; font-weight: 900; font-size: clamp(0.88rem, 0.98vw, 1.1rem); }
    .day-check-sat { color: #c084fc; font-weight: 900; font-size: clamp(0.88rem, 0.98vw, 1.1rem); }
    .day-off { color: #1e293b; font-size: 0.8rem; }

    .row-COMPLETADO { opacity: 0.5; }
</style>
""",
    unsafe_allow_html=True,
)


# ---------------------------------------------------------
# RENDERING DE TABLERO (TV 43" - DIRECTO A TABLA)
# ---------------------------------------------------------
@st.fragment(run_every=10)
def renderizar_tablero_vertical():
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
    ["📱 Tablero TV (En Vivo)", "⚡ Control de Ruta Hoy", "⚙️ Panel de Gestión"],
)

if modo == "📱 Tablero TV (En Vivo)":
  renderizar_tablero_vertical()

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