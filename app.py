"""
Sistema de Control Logístico y Distribución en Streamlit
Diseño en 2 Columnas Fijas, Optimizado para 100 Ubicaciones en TV
"""

import os
import sqlite3
import tempfile
import time
from datetime import datetime
import pandas as pd
import streamlit as st

# ---------------------------------------------------------
# CONFIGURACIÓN DE PÁGINA
# ---------------------------------------------------------
st.set_page_config(
    page_title='Tablero Logístico TV',
    page_icon='🚚',
    layout='wide',
    initial_sidebar_state='collapsed',
)

DB_NAME = os.path.join(tempfile.gettempdir(), 'logistica_streamlit.db')

MOTORIZADOS_CONFIG = {
    'Eduard': {'code': 'ED', 'bg': '#2563eb', 'color': '#ffffff'},
    'Freduard': {'code': 'FR', 'bg': '#7c3aed', 'color': '#ffffff'},
    'Alejandro': {'code': 'AL', 'bg': '#059669', 'color': '#ffffff'},
    'Gustavo': {'code': 'GU', 'bg': '#d97706', 'color': '#ffffff'},
    'Sin Asignar': {'code': '--', 'bg': '#334155', 'color': '#94a3b8'},
}

MOTORIZADOS_DISPONIBLES = list(MOTORIZADOS_CONFIG.keys())


# ---------------------------------------------------------
# BASE DE DATOS SQLITE
# ---------------------------------------------------------
def get_db_connection():
  conn = sqlite3.connect(DB_NAME, check_same_thread=False)
  conn.row_factory = sqlite3.Row
  return conn


def init_db(force_reset=False):
  conn = get_db_connection()
  cursor = conn.cursor()

  if force_reset:
    cursor.execute('DROP TABLE IF EXISTS maquinas')

  cursor.execute("""
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
    """)

  cursor.execute('SELECT COUNT(*) FROM maquinas')
  total = cursor.fetchone()[0]

  # Si la base de datos está vacía, genera datos de prueba
  if total == 0:
    motos = ['Eduard', 'Freduard', 'Alejandro', 'Gustavo']
    sample_locations = []
    for i in range(1, 101):
      m_nombre = f'Ubicación {i:03d}'
      m_resp = motos[i % len(motos)]
      sample_locations.append((
          m_nombre,
          m_resp,
          1 if i % 2 == 0 else 0,
          1 if i % 3 == 0 else 0,
          1 if i % 4 == 0 else 0,
          1 if i % 5 == 0 else 0,
          1 if i % 2 != 0 else 0,
          1 if i % 6 == 0 else 0,
          '',
      ))

    cursor.executemany(
        """
            INSERT INTO maquinas (nombre, motorizado, lunes, martes, miercoles, jueves, viernes, sabado, observaciones)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        sample_locations,
    )
    conn.commit()

  conn.close()


init_db()


def cargar_maquinas():
  conn = get_db_connection()
  df = pd.read_sql_query('SELECT * FROM maquinas ORDER BY id ASC', conn)
  conn.close()
  return df


def agregar_maquina(
    nombre, motorizado, lunes, martes, miercoles, jueves, viernes, sabado
):
  conn = get_db_connection()
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
  conn.close()


def actualizar_maquina(
    m_id, nombre, motorizado, lunes, martes, miercoles, jueves, viernes, sabado
):
  conn = get_db_connection()
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
  conn.close()


def eliminar_maquina(m_id):
  conn = get_db_connection()
  cursor = conn.cursor()
  cursor.execute('DELETE FROM maquinas WHERE id=?', (m_id,))
  conn.commit()
  conn.close()


# ---------------------------------------------------------
# ESTILOS CSS (LIMPIO Y DE ALTO CONTRASTE)
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
    
    .block-container {
        padding-top: 0.2rem !important;
        padding-bottom: 0.1rem !important;
        padding-left: 0.3rem !important;
        padding-right: 0.3rem !important;
        max-width: 100% !important;
    }
    
    .stApp { background-color: #0b1329; color: #f8fafc; }
    
    /* Encabezado Principal */
    .live-header {
        background-color: #152238;
        padding: 0.3rem 0.8rem;
        border-radius: 6px;
        margin-bottom: 0.3rem;
        border: 1px solid #1e293b;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .live-badge {
        background-color: #ef4444;
        color: white;
        padding: 0.1rem 0.4rem;
        border-radius: 4px;
        font-weight: 800;
        font-size: 0.75rem;
    }
    .live-title {
        font-size: 1.1rem;
        font-weight: 800;
        color: #f8fafc;
        margin-left: 0.5rem;
    }
    .live-time {
        font-size: 0.85rem;
        font-weight: 700;
        color: #38bdf8;
    }
    
    /* Leyenda */
    .legend-box {
        background-color: #152238;
        border: 1px solid #1e293b;
        border-radius: 6px;
        padding: 2px 8px;
        margin-bottom: 4px;
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 15px;
    }
    .legend-item {
        display: inline-flex;
        align-items: center;
        font-size: 0.75rem;
        font-weight: 700;
        color: #cbd5e1;
    }
    .moto-badge {
        display: inline-block;
        padding: 1px 5px;
        border-radius: 3px;
        font-weight: 900;
        font-size: 0.68rem;
        text-align: center;
        margin-right: 3px;
    }
    
    /* Estructura de Tabla Ultra-Compacta para 2 Bloques */
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
        font-size: 0.7rem;
        font-weight: 800;
        padding: 0.25rem 0.2rem;
        border-bottom: 2px solid #1e293b;
        text-align: left;
    }
    .tv-table th.center-header { text-align: center; }
    
    .tv-table td {
        padding: 0.12rem 0.3rem !important;
        border-bottom: 1px solid #1a273e;
        vertical-align: middle;
        white-space: nowrap;
    }
    .location-name {
        font-size: 0.8rem;
        font-weight: 800;
        color: #ffffff !important;
    }
    .tv-table tr:nth-child(even) { background-color: #0e172a; }
    
    /* Indicadores Limpios */
    .day-check { color: #38bdf8; font-weight: 900; font-size: 0.85rem; }
    .day-check-sat { color: #a855f7; font-weight: 900; font-size: 0.85rem; }
    .day-off { color: #1e293b; font-size: 0.7rem; }
</style>
""",
    unsafe_allow_html=True,
)

# ---------------------------------------------------------
# NAVEGACIÓN EN SIDEBAR
# ---------------------------------------------------------
st.sidebar.title('🎛️ NAVEGACIÓN')
modo = st.sidebar.radio(
    'Seleccionar Vista:', ['📱 Tablero Multi-Columna', '⚙️ Panel de Control']
)


# ---------------------------------------------------------
# TABLERO EN VIVO (2 BLOQUES)
# ---------------------------------------------------------
@st.fragment(run_every=10)
def renderizar_tablero_dos_bloques():
  hora_actual = datetime.now().strftime('%H:%M:%S')
  fecha_actual = datetime.now().strftime('%d/%m/%Y')

  # 1. Header
  st.markdown(
      f"""
    <div class="live-header">
        <div><span class="live-badge">● EN VIVO</span> <span class="live-title">CONTROL DE RECARGAS Y LOGÍSTICA</span></div>
        <div class="live-time">⏱️ {hora_actual} <span style="font-size: 0.75rem; color: #64748b; margin-left: 5px;">({fecha_actual})</span></div>
    </div>
    """,
      unsafe_allow_html=True,
  )

  # 2. Leyenda
  legend_html = '<div class="legend-box">'
  for nombre, cfg in MOTORIZADOS_CONFIG.items():
    legend_html += f'<div class="legend-item"><span class="moto-badge" style="background-color: {cfg["bg"]}; color: {cfg["color"]};">{cfg["code"]}</span> {nombre}</div>'
  legend_html += '</div>'
  st.markdown(legend_html, unsafe_allow_html=True)

  # 3. Distribución en exactamente 2 Bloques
  df_maquinas = cargar_maquinas()
  total_registros = len(df_maquinas)

  cols_st = st.columns(2)
  chunk_size = (total_registros + 1) // 2

  def get_cell(active, is_sat=False):
    if active:
      cls = 'day-check-sat' if is_sat else 'day-check'
      return f'<span class="{cls}">✓</span>'
    return '<span class="day-off">-</span>'

  def get_moto_badge(motorizado_nombre):
    cfg = MOTORIZADOS_CONFIG.get(
        motorizado_nombre, MOTORIZADOS_CONFIG['Sin Asignar']
    )
    return f'<span class="moto-badge" style="background-color: {cfg["bg"]}; color: {cfg["color"]};">{cfg["code"]}</span>'

  def generar_tabla_html(sub_df):
    html_rows = ''
    for _, m in sub_df.iterrows():
      badge_moto = get_moto_badge(m['motorizado'])
      c_l = get_cell(m['lunes'])
      c_m = get_cell(m['martes'])
      c_x = get_cell(m['miercoles'])
      c_j = get_cell(m['jueves'])
      c_v = get_cell(m['viernes'])
      c_s = get_cell(m['sabado'], is_sat=True)

      html_rows += f'<tr><td class="location-name">{m["nombre"]}</td><td style="text-align: center;">{badge_moto}</td><td style="text-align: center;">{c_l}</td><td style="text-align: center;">{c_m}</td><td style="text-align: center;">{c_x}</td><td style="text-align: center;">{c_j}</td><td style="text-align: center;">{c_v}</td><td style="text-align: center;">{c_s}</td></tr>'

    return f'<div class="tv-container"><table class="tv-table"><thead><tr><th style="width: 46%;">UBICACIÓN</th><th class="center-header" style="width: 12%;">RESP.</th><th class="center-header" style="width: 7%;">L</th><th class="center-header" style="width: 7%;">M</th><th class="center-header" style="width: 7%;">X</th><th class="center-header" style="width: 7%;">J</th><th class="center-header" style="width: 7%;">V</th><th class="center-header" style="width: 7%;">S</th></tr></thead><tbody>{html_rows}</tbody></table></div>'

  for i in range(2):
    start_idx = i * chunk_size
    end_idx = min((i + 1) * chunk_size, total_registros)
    sub_df = df_maquinas.iloc[start_idx:end_idx]

    with cols_st[i]:
      if not sub_df.empty:
        st.markdown(generar_tabla_html(sub_df), unsafe_allow_html=True)


# ---------------------------------------------------------
# PANEL DE CONTROL (EDICIÓN Y ADMINISTRACIÓN)
# ---------------------------------------------------------
if modo == '📱 Tablero Multi-Columna':
  renderizar_tablero_dos_bloques()

elif modo == '⚙️ Panel de Control':
  st.title('⚙️ Panel de Gestión')
  st.markdown('---')

  pin_ingresado = st.sidebar.text_input(
      'Clave Supervisor:', type='password', value='1234'
  )

  if pin_ingresado != '1234':
    st.warning('🔒 Ingrese la clave de supervisor correcta para editar.')
  else:
    st.success('🔓 Acceso concedido.')

    if st.sidebar.button('🔄 Restablecer 100 Ubicaciones Pruebas'):
      init_db(force_reset=True)
      st.sidebar.success('¡Base de datos restablecida a 100 registros!')
      st.rerun()

    col_form, col_tabla = st.columns([1, 2])

    with col_form:
      st.subheader('➕ Agregar Ubicación')
      with st.form('form_agregar', clear_on_submit=True):
        nombre_nuevo = st.text_input('Nombre de Ubicación:')
        moto_nuevo = st.selectbox(
            'Motorizado Asignado:', MOTORIZADOS_DISPONIBLES, index=0
        )

        st.write('**Días de Recarga:**')
        c_l, c_m, c_x, c_j, c_v, c_s = st.columns(6)
        l_val = c_l.checkbox('L', value=True)
        m_val = c_m.checkbox('M', value=False)
        x_val = c_x.checkbox('X', value=False)
        j_val = c_j.checkbox('J', value=False)
        v_val = c_v.checkbox('V', value=False)
        s_val = c_s.checkbox('S', value=False)

        btn_guardar = st.form_submit_button('💾 Guardar')

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
          st.success('Ubicación agregada.')
          st.rerun()

    with col_tabla:
      st.subheader('📋 Modificar / Eliminar')
      df = cargar_maquinas()

      for index, row in df.iterrows():
        cfg = MOTORIZADOS_CONFIG.get(
            row['motorizado'], MOTORIZADOS_CONFIG['Sin Asignar']
        )
        with st.expander(
            f"📌 {row['nombre']} | [{cfg['code']}] {row['motorizado']}"
        ):
          with st.form(f"form_edit_{row['id']}"):
            e_nombre = st.text_input('Ubicación:', value=row['nombre'])

            idx_moto = (
                MOTORIZADOS_DISPONIBLES.index(row['motorizado'])
                if row['motorizado'] in MOTORIZADOS_DISPONIBLES
                else 4
            )
            e_moto = st.selectbox(
                'Motorizado:',
                MOTORIZADOS_DISPONIBLES,
                index=idx_moto,
                key=f"moto_{row['id']}",
            )

            st.write('**Días Activos:**')
            d1, d2, d3, d4, d5, d6 = st.columns(6)
            e_l = d1.checkbox(
                'L', value=bool(row['lunes']), key=f"l_{row['id']}"
            )
            e_m = d2.checkbox(
                'M', value=bool(row['martes']), key=f"m_{row['id']}"
            )
            e_x = d3.checkbox(
                'X', value=bool(row['miercoles']), key=f"x_{row['id']}"
            )
            e_j = d4.checkbox(
                'J', value=bool(row['jueves']), key=f"j_{row['id']}"
            )
            e_v = d5.checkbox(
                'V', value=bool(row['viernes']), key=f"v_{row['id']}"
            )
            e_s = d6.checkbox(
                'S', value=bool(row['sabado']), key=f"s_{row['id']}"
            )

            b1, b2 = st.columns(2)
            if b1.form_submit_button('💾 Actualizar'):
              actualizar_maquina(
                  row['id'],
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

            if b2.form_submit_button('🗑️ Eliminar'):
              eliminar_maquina(row['id'])
              st.rerun()