"""
Sistema de Control Logístico y Distribución en Streamlit
Diseño Multi-Columna Vertical para 61+ Ubicaciones en TV
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
    page_title='Tablero Logístico Multi-Columna',
    page_icon='🚚',
    layout='wide',
    initial_sidebar_state='expanded',
)

DB_NAME = os.path.join(tempfile.gettempdir(), 'logistica_streamlit.db')

# Mapeo de Leyendas (Iniciales, Nombre, Color de Fondo, Color de Texto)
MOTORIZADOS_CONFIG = {
    'Eduard': {'code': 'ED', 'bg': '#2563eb', 'color': '#ffffff'},
    'Freduard': {'code': 'FR', 'bg': '#7c3aed', 'color': '#ffffff'},
    'Alejandro': {'code': 'AL', 'bg': '#059669', 'color': '#ffffff'},
    'Gustavo': {'code': 'GU', 'bg': '#d97706', 'color': '#ffffff'},
    'Sin Asignar': {'code': '--', 'bg': '#475569', 'color': '#cbd5e1'},
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

  # Si se solicita reset o la tabla no existe, recreamos la estructura
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
  total_registros = cursor.fetchone()[0]

  # Carga de las 61 máquinas reales proporcionadas
  if total_registros == 0 or force_reset:
    cursor.execute('DELETE FROM maquinas')

    sample_locations = [
        ('Unimet PB', 'Eduard', 1, 0, 1, 0, 0, 0, ''),
        ('Unimet LAB', 'Eduard', 0, 1, 0, 1, 0, 0, ''),
        ('Unimet EM', 'Eduard', 1, 0, 0, 0, 1, 0, ''),
        ('UCV ING', 'Alejandro', 1, 0, 1, 0, 0, 0, ''),
        ('UCV COMP', 'Alejandro', 0, 1, 0, 1, 0, 0, ''),
        ('UCAB CONVERT', 'Freduard', 0, 0, 1, 1, 0, 0, ''),
        ('UCAB LAB', 'Freduard', 0, 1, 0, 0, 1, 0, ''),
        ('UCAB P1', 'Freduard', 1, 0, 0, 0, 0, 0, ''),
        ('UCAB MEZ', 'Freduard', 0, 1, 0, 0, 0, 0, ''),
        ('UCAB M3', 'Freduard', 0, 0, 1, 0, 0, 0, ''),
        ('USM', 'Alejandro', 1, 0, 1, 0, 1, 0, ''),
        ('MONTAÑA', 'Alejandro', 0, 0, 0, 1, 0, 0, ''),
        ('EURO S1', 'Gustavo', 1, 0, 0, 1, 0, 0, ''),
        ('EURO S2', 'Gustavo', 0, 1, 0, 0, 1, 0, ''),
        ('TAMACO', 'Eduard', 0, 1, 0, 0, 0, 0, ''),
        ('TAMACA', 'Eduard', 0, 1, 0, 0, 0, 0, ''),
        ('HUMBOLDT', 'Alejandro', 1, 0, 0, 0, 0, 0, ''),
        ('GOLD DATA', 'Gustavo', 0, 0, 1, 0, 0, 0, ''),
        ('PAGO DIRECTO', 'Gustavo', 1, 0, 1, 0, 1, 0, ''),
        ('CUBITT', 'Alejandro', 0, 1, 0, 1, 0, 0, ''),
        ('KURIOS', 'Eduard', 0, 0, 0, 0, 1, 0, ''),
        ('CASHEA P9', 'Freduard', 1, 0, 1, 0, 1, 0, ''),
        ('CASHEA P18', 'Freduard', 1, 0, 1, 0, 1, 0, ''),
        ('DICAM', 'Alejandro', 0, 1, 0, 0, 0, 0, ''),
        ('FISA', 'Gustavo', 0, 0, 1, 0, 0, 0, ''),
        ('DOMESA', 'Eduard', 1, 1, 1, 1, 1, 0, ''),
        ('TU GRUERO', 'Alejandro', 0, 0, 0, 1, 0, 0, ''),
        ('UNION RADIO', 'Gustavo', 1, 0, 0, 1, 0, 0, ''),
        ('FORUM P7', 'Freduard', 0, 1, 0, 0, 1, 0, ''),
        ('FORUM P15', 'Freduard', 0, 1, 0, 0, 1, 0, ''),
        ('BANGENTE', 'Alejandro', 1, 0, 1, 0, 0, 0, ''),
        ('PROVINCIAL', 'Gustavo', 1, 0, 0, 0, 0, 0, ''),
        ('TRANRED', 'Eduard', 0, 0, 1, 0, 0, 0, ''),
        ('ROBIN', 'Alejandro', 1, 0, 1, 0, 0, 0, ''),
        ('CALLCENTER DRCC', 'Gustavo', 1, 0, 0, 0, 0, 0, ''),
        ('DUNCAN', 'Eduard', 0, 0, 0, 1, 0, 0, ''),
        ('ADROMEDA', 'Freduard', 1, 0, 0, 1, 0, 0, ''),
        ('PEGASO', 'Alejandro', 0, 1, 0, 0, 0, 0, ''),
        ('TIO AMMI 1', 'Eduard', 1, 0, 1, 0, 0, 0, ''),
        ('TIO AMMI 2', 'Eduard', 0, 1, 0, 1, 0, 0, ''),
        ('RS1 RECEP', 'Gustavo', 1, 0, 0, 0, 1, 0, ''),
        ('RS2 COMED', 'Gustavo', 0, 1, 0, 1, 0, 0, ''),
        ('WECONNECT', 'Alejandro', 0, 0, 1, 0, 1, 0, ''),
        ('CEMENTERIO', 'Freduard', 1, 0, 1, 0, 0, 0, ''),
        ('HEBRAICA', 'Freduard', 0, 1, 0, 1, 0, 0, ''),
        ('POLICLINICA P3', 'Eduard', 1, 0, 1, 0, 1, 0, ''),
        ('POLICLINICA P4', 'Eduard', 1, 0, 1, 0, 1, 0, ''),
        ('FLORESTA EM', 'Gustavo', 0, 1, 0, 0, 1, 0, ''),
        ('FLORESTA P3', 'Gustavo', 0, 1, 0, 0, 1, 0, ''),
        ('AVILA ADULT', 'Alejandro', 1, 0, 0, 1, 0, 0, ''),
        ('AVILA PEDT', 'Alejandro', 1, 0, 0, 1, 0, 0, ''),
        ('SANATRIX', 'Freduard', 0, 1, 0, 1, 0, 0, ''),
        ('VENE CHACAO', 'Eduard', 1, 0, 1, 0, 0, 0, ''),
        ('VENE ALTAMIRA', 'Eduard', 0, 1, 0, 1, 0, 0, ''),
        ('VENE CANDELARIA', 'Eduard', 1, 0, 1, 0, 0, 0, ''),
        ('FLORIDA', 'Gustavo', 0, 0, 1, 0, 1, 0, ''),
        ('CCS S1', 'Alejandro', 1, 0, 0, 1, 0, 0, ''),
        ('CCS S2', 'Alejandro', 0, 1, 0, 0, 1, 0, ''),
        ('FENIX', 'Freduard', 1, 0, 1, 0, 0, 0, ''),
        ('OFICENTRO 1', 'Gustavo', 1, 0, 0, 1, 0, 0, ''),
        ('OFICENTRO 2', 'Gustavo', 0, 1, 0, 0, 1, 0, ''),
    ]

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
# ESTILOS CSS
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
    [data-testid="stSidebarCollapseButton"], 
    [data-testid="collapsedControl"] {
        visibility: visible !important;
        display: block !important;
        color: #f8fafc !important;
        background-color: #1e293b !important;
        border-radius: 6px !important;
    }
    
    .block-container {
        padding-top: 0.5rem !important;
        padding-bottom: 0.2rem !important;
        padding-left: 0.4rem !important;
        padding-right: 0.4rem !important;
        max-width: 100% !important;
    }
    
    .stApp { background-color: #0f172a; color: #f8fafc; }
    
    .live-header-vertical {
        background-color: #1e293b;
        padding: 0.3rem 0.6rem;
        border-radius: 6px;
        margin-bottom: 0.3rem;
        border: 1px solid #334155;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .live-badge {
        background-color: #ef4444;
        color: white;
        padding: 0.1rem 0.4rem;
        border-radius: 10px;
        font-weight: bold;
        font-size: 0.75rem;
    }
    .live-title {
        font-size: 1.05rem;
        font-weight: 800;
        color: #f1f5f9;
    }
    .live-time {
        font-size: 0.85rem;
        font-weight: 700;
        color: #38bdf8;
    }
    
    .legend-box {
        background-color: #1e293b;
        border: 1px solid #334155;
        border-radius: 6px;
        padding: 4px 8px;
        margin-bottom: 6px;
        display: flex;
        flex-wrap: wrap;
        justify-content: center;
        align-items: center;
        gap: 10px;
    }
    .legend-item {
        display: inline-flex;
        align-items: center;
        font-size: 0.75rem;
        font-weight: 700;
        color: #e2e8f0;
    }
    .moto-badge {
        display: inline-block;
        padding: 1px 5px;
        border-radius: 4px;
        font-weight: 900;
        font-size: 0.7rem;
        text-align: center;
        min-width: 22px;
        margin-right: 3px;
    }
    
    .tv-container {
        width: 100%;
        background-color: #1e293b;
        border-radius: 6px;
        padding: 2px;
        border: 1px solid #334155;
    }
    .tv-table {
        width: 100%;
        border-collapse: collapse;
        color: #f8fafc;
        font-family: 'Segoe UI', Arial, sans-serif;
    }
    .tv-table th {
        background-color: #0f172a;
        color: #38bdf8;
        font-size: 0.75rem;
        font-weight: 800;
        text-transform: uppercase;
        padding: 0.25rem 0.2rem;
        border-bottom: 2px solid #334155;
        text-align: left;
    }
    .tv-table th.center-header {
        text-align: center;
    }
    
    .tv-table td {
        padding: 0.12rem 0.25rem !important;
        border-bottom: 1px solid #334155;
        font-size: 0.78rem !important;
        font-weight: 700 !important;
        color: #ffffff !important;
        vertical-align: middle;
        line-height: 1.1;
        white-space: nowrap;
    }
    .tv-table tr:nth-child(even) { background-color: #162032; }
    
    .day-pill {
        display: inline-flex;
        width: 18px;
        height: 18px;
        align-items: center;
        justify-content: center;
        border-radius: 3px;
        font-weight: 800;
        font-size: 0.65rem;
        background-color: #0284c7;
        color: #ffffff;
    }
    .day-pill-sat { background-color: #7c3aed; }
    .day-empty { color: #475569; font-weight: 400; font-size: 0.7rem; }
</style>
""",
    unsafe_allow_html=True,
)

# ---------------------------------------------------------
# NAVEGACIÓN
# ---------------------------------------------------------
st.sidebar.title('🎛️ NAVEGACIÓN')
modo = st.sidebar.radio(
    'Seleccionar Vista:', ['📱 Tablero Multi-Columna', '⚙️ Panel de Control']
)


# ---------------------------------------------------------
# TABLERO MULTI-COLUMNA EN VIVO
# ---------------------------------------------------------
@st.fragment(run_every=10)
def renderizar_tablero_vertical():
  hora_actual = datetime.now().strftime('%H:%M:%S')
  fecha_actual = datetime.now().strftime('%d/%m/%Y')

  st.markdown(
      f"""
    <div class="live-header-vertical">
        <div><span class="live-badge">● EN VIVO</span> <span class="live-title">PROGRAMACIÓN DE RECARGA</span></div>
        <div class="live-time">⏱️ {hora_actual} <span style="font-size: 0.75rem; color: #94a3b8;">({fecha_actual})</span></div>
    </div>
    """,
      unsafe_allow_html=True,
  )

  legend_html = '<div class="legend-box">'
  for nombre, cfg in MOTORIZADOS_CONFIG.items():
    legend_html += f'<div class="legend-item"><span class="moto-badge" style="background-color: {cfg["bg"]}; color: {cfg["color"]};">{cfg["code"]}</span> {nombre}</div>'
  legend_html += '</div>'
  st.markdown(legend_html, unsafe_allow_html=True)

  df_maquinas = cargar_maquinas()
  total_registros = len(df_maquinas)

  # Si hay más de 36 registros se divide en 3 columnas
  if total_registros <= 36:
    num_cols = 2
  else:
    num_cols = 3

  cols_st = st.columns(num_cols)

  def get_cell(active, is_sat=False):
    if active:
      cls = 'day-pill day-pill-sat' if is_sat else 'day-pill'
      return f'<span class="{cls}">✓</span>'
    return '<span class="day-empty">-</span>'

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

      html_rows += f'<tr><td style="font-weight: 800; color: #ffffff !important;">{m["nombre"]}</td><td style="text-align: center;">{badge_moto}</td><td style="text-align: center;">{c_l}</td><td style="text-align: center;">{c_m}</td><td style="text-align: center;">{c_x}</td><td style="text-align: center;">{c_j}</td><td style="text-align: center;">{c_v}</td><td style="text-align: center;">{c_s}</td></tr>'

    return f'<div class="tv-container"><table class="tv-table"><thead><tr><th style="width: 44%;">UBICACIÓN</th><th class="center-header" style="width: 14%;">RESP.</th><th class="center-header" style="width: 7%;">L</th><th class="center-header" style="width: 7%;">M</th><th class="center-header" style="width: 7%;">X</th><th class="center-header" style="width: 7%;">J</th><th class="center-header" style="width: 7%;">V</th><th class="center-header" style="width: 7%;">S</th></tr></thead><tbody>{html_rows}</tbody></table></div>'

  chunk_size = (total_registros + num_cols - 1) // num_cols

  for i in range(num_cols):
    start_idx = i * chunk_size
    end_idx = min((i + 1) * chunk_size, total_registros)
    sub_df = df_maquinas.iloc[start_idx:end_idx]

    with cols_st[i]:
      if not sub_df.empty:
        st.markdown(generar_tabla_html(sub_df), unsafe_allow_html=True)


# ---------------------------------------------------------
# VISTAS PRINCIPALES
# ---------------------------------------------------------
if modo == '📱 Tablero Multi-Columna':
  renderizar_tablero_vertical()

elif modo == '⚙️ Panel de Control':
  st.title('⚙️ Panel de Gestión')
  st.markdown('---')

  pin_ingresado = st.sidebar.text_input(
      'Clave Supervisor:', type='password', value='1234'
  )

  if pin_ingresado != '1234':
    st.warning('🔒 Ingrese la clave de supervisor correcta para editar.')
  else:
    st.success('🔓 Acceso concedido como Supervisor.')

    if st.sidebar.button('🔄 Restablecer Carga Completa (61)'):
      with st.spinner(
          '⏳ Cargando lista completa de 61 máquinas en la base de datos...'
      ):
        time.sleep(0.5)
        init_db(force_reset=True)
      st.sidebar.success('¡Base de datos restablecida con las 61 máquinas!')
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

        btn_guardar = st.form_submit_button('💾 Guardar Ubicación')

        if btn_guardar:
          if nombre_nuevo.strip():
            with st.spinner(f"⏳ Guardando '{nombre_nuevo}'..."):
              time.sleep(0.3)
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
            st.success(f"Ubicación '{nombre_nuevo}' guardada con éxito.")
            st.rerun()
          else:
            st.error('El nombre no puede estar vacío.')

    with col_tabla:
      st.subheader('📋 Modificar / Asignar Existentes')
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

            col_b1, col_b2 = st.columns([1, 1])
            with col_b1:
              btn_actualizar = st.form_submit_button('💾 Actualizar')
            with col_b2:
              btn_eliminar = st.form_submit_button('🗑️ Eliminar')

            if btn_actualizar:
              with st.spinner(f"⏳ Actualizando '{e_nombre}'..."):
                time.sleep(0.3)
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
              st.success('Cambios guardados.')
              st.rerun()

            if btn_eliminar:
              with st.spinner('⏳ Eliminando registro...'):
                time.sleep(0.3)
                eliminar_maquina(row['id'])
              st.warning('Registro eliminado.')
              st.rerun()