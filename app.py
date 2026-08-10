"""
Sistema de Control Logístico y Distribución en Streamlit
Diseño Vertical Rotado por CSS - Versión Optimizada
"""

import os
import sqlite3
import tempfile
from datetime import datetime
import pandas as pd
import streamlit as st

# ---------------------------------------------------------
# CONFIGURACIÓN DE PÁGINA
# ---------------------------------------------------------
st.set_page_config(
    page_title="Tablero Logístico Vertical",
    page_icon="🚚",
    layout="centered",
    initial_sidebar_state="collapsed",
)

DB_NAME = os.path.join(tempfile.gettempdir(), "logistica_streamlit_v2.db")
SUPERVISOR_PIN = st.secrets.get("SUPERVISOR_PIN", "1234")

MOTORIZADOS_CONFIG = {
    "Eduard": {"code": "ED", "bg": "#2563eb", "color": "#ffffff"},
    "Freduard": {"code": "FR", "bg": "#7c3aed", "color": "#ffffff"},
    "Alejandro": {"code": "AL", "bg": "#059669", "color": "#ffffff"},
    "Gustavo": {"code": "GU", "bg": "#d97706", "color": "#ffffff"},
    "Sin Asignar": {"code": "--", "bg": "#334155", "color": "#94a3b8"},
}

MOTORIZADOS_DISPONIBLES = list(MOTORIZADOS_CONFIG.keys())

# ---------------------------------------------------------
# LISTA REAL DE 61 MÁQUINAS/UBICACIONES
# ---------------------------------------------------------
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
    ("ADROMEDA", "Alejandro", 1, 0, 0, 0, 1, 0, ""),
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
# BASE DE DATOS SQLITE
# ---------------------------------------------------------
def get_db_connection():
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(force_reset=False):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        if force_reset:
            cursor.execute("DROP TABLE IF EXISTS maquinas")

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS maquinas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                motorizado TEXT DEFAULT 'Sin Asignar',
                lunes INTEGER DEFAULT 0,
                martes INTEGER DEFAULT 0,
                miercoles INTEGER DEFAULT 0,
                jueves INTEGER DEFAULT 0,
                viernes INTEGER DEFAULT 0,
                sabado INTEGER DEFAULT 0,
                observaciones TEXT DEFAULT ''
            )
            """
        )

        cursor.execute("SELECT COUNT(*) FROM maquinas")
        total = cursor.fetchone()[0]

        if total == 0 or force_reset:
            cursor.execute("DELETE FROM maquinas")
            cursor.executemany(
                """
                INSERT INTO maquinas (nombre, motorizado, lunes, martes, miercoles, jueves, viernes, sabado, observaciones)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                LISTA_REAL_MAQUINAS,
            )
            conn.commit()


init_db()


def cargar_maquinas():
    with get_db_connection() as conn:
        return pd.read_sql_query("SELECT * FROM maquinas ORDER BY id ASC", conn)


def agregar_maquina(nombre, motorizado, lunes, martes, miercoles, jueves, viernes, sabado):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO maquinas (nombre, motorizado, lunes, martes, miercoles, jueves, viernes, sabado, observaciones)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, '')
            """,
            (
                nombre,
                motorizado,
                int(lunes),
                int(martes),
                int(miercoles),
                int(jueves),
                int(viernes),
                int(sabado),
            ),
        )
        conn.commit()


def actualizar_maquina(m_id, nombre, motorizado, lunes, martes, miercoles, jueves, viernes, sabado):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE maquinas SET nombre=?, motorizado=?, lunes=?, martes=?, miercoles=?, jueves=?, viernes=?, sabado=?
            WHERE id=?
            """,
            (
                nombre,
                motorizado,
                int(lunes),
                int(martes),
                int(miercoles),
                int(jueves),
                int(viernes),
                int(sabado),
                m_id,
            ),
        )
        conn.commit()


def eliminar_maquina(m_id):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM maquinas WHERE id=?", (m_id,))
        conn.commit()


# ---------------------------------------------------------
# ESTILOS CSS CON ROTACIÓN Y FORMATO VERTICAL
# ---------------------------------------------------------
st.markdown(
    """
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    [data-testid="stHeader"] {
        background-color: transparent !important;
        z-index: 100000 !important;
    }
    
    .stApp { 
        background-color: #0b1329; 
        color: #f8fafc; 
    }

    @media screen and (min-width: 900px) {
        .stApp {
            transform: rotate(-90deg);
            transform-origin: center center;
            width: 100vh !important;
            height: 100vw !important;
            position: absolute;
            top: 50%;
            left: 50%;
            margin-top: -50vw;
            margin-left: -50vh;
            overflow-x: hidden;
        }
    }

    .block-container {
        padding-top: 0.2rem !important;
        padding-bottom: 0.2rem !important;
        padding-left: 0.3rem !important;
        padding-right: 0.3rem !important;
        max-width: 100% !important;
    }
    
    .live-header {
        background-color: #152238;
        padding: 0.4rem 0.6rem;
        border-radius: 6px;
        margin-bottom: 0.3rem;
        border: 1px solid #1e293b;
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 3px;
    }
    .live-badge {
        background-color: #ef4444;
        color: white;
        padding: 0.1rem 0.5rem;
        border-radius: 4px;
        font-weight: 800;
        font-size: 0.75rem;
    }
    .live-title {
        font-size: 1.2rem;
        font-weight: 800;
        color: #f8fafc;
        text-align: center;
    }
    .live-time {
        font-size: 0.95rem;
        font-weight: 700;
        color: #38bdf8;
    }
    
    .legend-box {
        background-color: #152238;
        border: 1px solid #1e293b;
        border-radius: 6px;
        padding: 6px;
        margin-bottom: 6px;
        display: flex;
        justify-content: space-around;
        align-items: center;
        flex-wrap: wrap;
        gap: 4px;
    }
    .legend-item {
        display: inline-flex;
        align-items: center;
        font-size: 0.8rem;
        font-weight: 700;
        color: #cbd5e1;
    }
    .moto-badge {
        display: inline-block;
        padding: 2px 6px;
        border-radius: 3px;
        font-weight: 900;
        font-size: 0.75rem;
        text-align: center;
        margin-right: 4px;
    }
    
    .tv-container {
        width: 100%;
        background-color: #111c30;
        border-radius: 6px;
        border: 1px solid #1e293b;
        overflow: hidden;
    }
    .tv-table {
        width: 100%;
        border-collapse: collapse;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    .tv-table th {
        background-color: #0b1329;
        color: #64748b;
        font-size: 0.8rem;
        font-weight: 800;
        padding: 0.35rem 0.2rem;
        border-bottom: 2px solid #1e293b;
        text-align: left;
    }
    .tv-table th.center-header { text-align: center; }
    
    .tv-table td {
        padding: 0.25rem 0.3rem !important;
        border-bottom: 1px solid #172338;
        vertical-align: middle;
        white-space: nowrap;
    }
    .location-name {
        font-size: 0.9rem;
        font-weight: 800;
        color: #ffffff !important;
    }
    .tv-table tr:nth-child(even) { background-color: #0d1627; }
    
    .day-check { color: #38bdf8; font-weight: 900; font-size: 0.9rem; }
    .day-check-sat { color: #a855f7; font-weight: 900; font-size: 0.9rem; }
    .day-off { color: #1e293b; font-size: 0.75rem; }
</style>
""",
    unsafe_allow_html=True,
)

# ---------------------------------------------------------
# NAVEGACIÓN
# ---------------------------------------------------------
st.sidebar.title("🎛️ NAVEGACIÓN")
modo = st.sidebar.radio("Seleccionar Vista:", ["📱 Tablero Vertical", "⚙️ Panel de Control"])


# ---------------------------------------------------------
# TABLERO EN VIVO
# ---------------------------------------------------------
@st.fragment(run_every=10)
def renderizar_tablero_vertical():
    hora_actual = datetime.now().strftime("%H:%M:%S")
    fecha_actual = datetime.now().strftime("%d/%m/%Y")

    st.markdown(
        f"""
    <div class="live-header">
        <div><span class="live-badge">● EN VIVO</span></div>
        <div class="live-title">CONTROL DE RECARGAS Y LOGÍSTICA</div>
        <div class="live-time">⏱️ {hora_actual} <span style="font-size: 0.8rem; color: #64748b;">({fecha_actual})</span></div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    legend_items = "".join(
        f'<div class="legend-item"><span class="moto-badge" style="background-color: {cfg["bg"]}; color: {cfg["color"]};">{cfg["code"]}</span> {nombre}</div>'
        for nombre, cfg in MOTORIZADOS_CONFIG.items()
    )
    st.markdown(f'<div class="legend-box">{legend_items}</div>', unsafe_allow_html=True)

    df_maquinas = cargar_maquinas()

    def get_cell(active, is_sat=False):
        if active:
            cls = "day-check-sat" if is_sat else "day-check"
            return f'<span class="{cls}">✓</span>'
        return '<span class="day-off">-</span>'

    def get_moto_badge(motorizado_nombre):
        cfg = MOTORIZADOS_CONFIG.get(motorizado_nombre, MOTORIZADOS_CONFIG["Sin Asignar"])
        return f'<span class="moto-badge" style="background-color: {cfg["bg"]}; color: {cfg["color"]};">{cfg["code"]}</span>'

    rows_list = []
    for _, m in df_maquinas.iterrows():
        badge_moto = get_moto_badge(m["motorizado"])
        c_l = get_cell(m["lunes"])
        c_m = get_cell(m["martes"])
        c_x = get_cell(m["miercoles"])
        c_j = get_cell(m["jueves"])
        c_v = get_cell(m["viernes"])
        c_s = get_cell(m["sabado"], is_sat=True)

        rows_list.append(
            f'<tr><td class="location-name">{m["nombre"]}</td>'
            f'<td style="text-align: center;">{badge_moto}</td>'
            f'<td style="text-align: center;">{c_l}</td>'
            f'<td style="text-align: center;">{c_m}</td>'
            f'<td style="text-align: center;">{c_x}</td>'
            f'<td style="text-align: center;">{c_j}</td>'
            f'<td style="text-align: center;">{c_v}</td>'
            f'<td style="text-align: center;">{c_s}</td></tr>'
        )

    html_rows = "".join(rows_list)
    tabla_completa = (
        f'<div class="tv-container"><table class="tv-table"><thead><tr>'
        f'<th style="width: 45%;">UBICACIÓN</th>'
        f'<th class="center-header" style="width: 13%;">RESP.</th>'
        f'<th class="center-header" style="width: 7%;">L</th>'
        f'<th class="center-header" style="width: 7%;">M</th>'
        f'<th class="center-header" style="width: 7%;">X</th>'
        f'<th class="center-header" style="width: 7%;">J</th>'
        f'<th class="center-header" style="width: 7%;">V</th>'
        f'<th class="center-header" style="width: 7%;">S</th>'
        f'</tr></thead><tbody>{html_rows}</tbody></table></div>'
    )

    st.markdown(tabla_completa, unsafe_allow_html=True)


# ---------------------------------------------------------
# PANEL DE CONTROL
# ---------------------------------------------------------
if modo == "📱 Tablero Vertical":
    renderizar_tablero_vertical()

elif modo == "⚙️ Panel de Control":
    st.title("⚙️ Panel de Gestión")
    st.markdown("---")

    pin_ingresado = st.sidebar.text_input("Clave Supervisor:", type="password")

    if pin_ingresado != SUPERVISOR_PIN:
        st.warning("🔒 Ingrese la clave de supervisor correcta para editar.")
    else:
        st.success("🔓 Acceso concedido.")

        if st.sidebar.button("🔄 Recargar las 61 Ubicaciones Iniciales"):
            init_db(force_reset=True)
            st.sidebar.success("¡Base de datos restablecida con éxito!")
            st.rerun()

        col_form, col_tabla = st.columns([1, 2])

        with col_form:
            st.subheader("➕ Agregar Nueva Ubicación")
            with st.form("form_agregar", clear_on_submit=True):
                nombre_nuevo = st.text_input("Nombre de Ubicación:")
                moto_nuevo = st.selectbox("Motorizado Asignado:", MOTORIZADOS_DISPONIBLES, index=0)

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
                        l_val,
                        m_val,
                        x_val,
                        j_val,
                        v_val,
                        s_val,
                    )
                    st.success("Ubicación agregada.")
                    st.rerun()

        with col_tabla:
            st.subheader("📋 Modificar / Eliminar")
            df = cargar_maquinas()

            for index, row in df.iterrows():
                cfg = MOTORIZADOS_CONFIG.get(row["motorizado"], MOTORIZADOS_CONFIG["Sin Asignar"])
                with st.expander(f"📌 {row['nombre']} | [{cfg['code']}] {row['motorizado']}"):
                    with st.form(f"form_edit_{row['id']}"):
                        e_nombre = st.text_input("Ubicación:", value=row["nombre"])

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
                        e_l = d1.checkbox("L", value=bool(row["lunes"]), key=f"l_{row['id']}")
                        e_m = d2.checkbox("M", value=bool(row["martes"]), key=f"m_{row['id']}")
                        e_x = d3.checkbox("X", value=bool(row["miercoles"]), key=f"x_{row['id']}")
                        e_j = d4.checkbox("J", value=bool(row["jueves"]), key=f"j_{row['id']}")
                        e_v = d5.checkbox("V", value=bool(row["viernes"]), key=f"v_{row['id']}")
                        e_s = d6.checkbox("S", value=bool(row["sabado"]), key=f"s_{row['id']}")

                        b1, b2 = st.columns(2)
                        if b1.form_submit_button("💾 Actualizar"):
                            actualizar_maquina(
                                row["id"],
                                e_nombre,
                                e_moto,
                                e_l,
                                e_m,
                                e_x,
                                e_j,
                                e_v,
                                e_s,
                            )
                            st.rerun()

                        if b2.form_submit_button("🗑️ Eliminar"):
                            eliminar_maquina(row["id"])
                            st.rerun()