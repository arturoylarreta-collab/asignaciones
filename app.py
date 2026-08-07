"""
Tablero Ejecutivo de Control Logístico y Distribución para TV
Diseño Prémium Estilizado con Recuadros Interativos en Tiempo Real
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

# Lista Maestra de las 61 Ubicaciones requeridas
LISTA_MAESTRA_61 = [
    'Unimet PB',
    'Unimet LAB',
    'Unimet EM',
    'UCV ING',
    'UCV COMP',
    'UCAB CONVERT',
    'UCAB LAB',
    'UCAB P1',
    'UCAB MEZ',
    'UCAB M3',
    'USM',
    'MONTAÑA',
    'EURO S1',
    'EURO S2',
    'TAMACO',
    'TAMACA',
    'HUMBOLDT',
    'GOLD DATA',
    'PAGO DIRECTO',
    'CUBITT',
    'KURIOS',
    'CASHEA P9',
    'CASHEA P18',
    'DICAM',
    'FISA',
    'DOMESA',
    'TU GRUERO',
    'UNION RADIO',
    'FORUM P7',
    'FORUM P15',
    'BANGENTE',
    'PROVINCIAL',
    'TRANRED',
    'ROBIN',
    'CALLCENTER DRCC',
    'DUNCAN',
    'ADROMEDA',
    'PEGASO',
    'TIO AMMI 1',
    'TIO AMMI 2',
    'RS1 RECEP',
    'RS2 COMED',
    'WECONNECT',
    'CEMENTERIO',
    'HEBRAICA',
    'POLICLINICA P3',
    'POLICLINICA P4',
    'FLORESTA EM',
    'FLORESTA P3',
    'AVILA ADULT',
    'AVILA PEDT',
    'SANATRIX',
    'VENE CHACAO',
    'VENE ALTAMIRA',
    'VENE CANDELARIA',
    'FLORIDA',
    'CCS S1',
    'CCS S2',
    'FENIX',
    'OFICENTRO 1',
    'OFICENTRO 2',
]

MOTORIZADOS_CONFIG = {
    'Eduard': {'code': 'ED', 'bg': '#2563eb', 'color': '#ffffff'},
    'Freduard': {'code': 'FR', 'bg': '#7c3aed', 'color': '#ffffff'},
    'Alejandro': {'code': 'AL', 'bg': '#059669', 'color': '#ffffff'},
    'Gustavo': {'code': 'GU', 'bg': '#d97706', 'color': '#ffffff'},
    'Sin Asignar': {'code': '--', 'bg': '#334155', 'color': '#94a3b8'},
}

MOTORIZADOS_DISPONIBLES = list(MOTORIZADOS_CONFIG.keys())


# ---------------------------------------------------------
# BASE DE DATOS Y AUTO-SINCRONIZACIÓN
# ---------------------------------------------------------
def get_db_connection():
  conn = sqlite3.connect(DB_NAME, check_same_thread=False)
  conn.row_factory = sqlite3.Row
  return conn


def init_db(force_reset=False):
  conn = get_db_connection()
  cursor = conn.cursor()

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

  if total_registros != len(LISTA_MAESTRA_61) or force_reset:
    cursor.execute('DELETE FROM maquinas')

    default_motos = ['Eduard', 'Freduard', 'Alejandro', 'Gustavo']
    sample_locations = []

    for idx, nombre in enumerate(LISTA_MAESTRA_61):
      assigned_moto = default_motos[idx % len(default_motos)]
      sample_locations.append((nombre, assigned_moto, 0, 0, 0, 0, 0, 0, ''))

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


def toggle_dia_db(m_id, columna_dia, valor_actual):
  conn = get_db_connection()
  cursor = conn.cursor()
  nuevo_valor = 0 if valor_actual == 1 else 1
  cursor.execute(
      f'UPDATE maquinas SET {columna_dia}=? WHERE id=?', (nuevo_valor, m_id)
  )
  conn.commit()
  conn.close()


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
# ESTILOS CSS ESTILIZADOS PARA PANTALLA TV
# ---------------------------------------------------------
st.markdown(
    """
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    [data-testid="stHeader"] { background-color: transparent !important; z-index: 100000 !important; }
    
    .block-container {
        padding-top: 0.2rem !important;
        padding-bottom: 0.1rem !important;
        padding-left: 0.3rem !important;
        padding-right: 0.3rem !important;
        max-width: 100% !important;
    }
    
    .stApp { background-color: #0b1329; color: #f8fafc; }
    
    /* Encabezado Principal */
    .tv-header {
        background: linear-gradient(90deg, #1e293b 0%, #0f172a 100%);
        padding: 0.35rem 0.8rem;
        border-radius: 8px;
        margin-bottom: 0.4rem;
        border: 1px solid #334155;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
    }
    .tv-badge {
        background-color: #ef4444;
        color: white;
        padding: 0.15rem 0.5rem;
        border-radius: 12px;
        font-weight: 800;
        font-size: 0.75rem;
        letter-spacing: 0.5px;
        animation: pulse 2s infinite;
    }
    .tv-title { font-size: 1.15rem; font-weight: 900; color: #ffffff; letter-spacing: 0.5px; }
    .tv-time { font-size: 0.9rem; font-weight: 800; color: #38bdf8; }
    
    /* Leyenda de Responsables */
    .legend-box {
        background-color: #1e293b;
        border: 1px solid #334155;
        border-radius: 6px;
        padding: 4px 10px;
        margin-bottom: 6px;
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 12px;
    }
    .legend-item { display: inline-flex; align-items: center; font-size: 0.75rem; font-weight: 800; color: #cbd5e1; gap: 5px; }
    .moto-badge {
        display: inline-block;
        padding: 2px 6px;
        border-radius: 4px;
        font-weight: 900;
        font-size: 0.7rem;
        text-align: center;
        min-width: 24px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.3);
    }
    
    /* Encabezados de Tabla */
    .table-header {
        background-color: #1e293b;
        color: #38bdf8;
        font-size: 0.75rem;
        font-weight: 800;
        padding: 5px 2px;
        border-radius: 4px;
        text-align: center;
        margin-bottom: 4px;
        border: 1px solid #334155;
    }
    
    .row-location {
        font-size: 0.78rem;
        font-weight: 800;
        color: #ffffff !important;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        padding-top: 3px;
    }
    
    /* Botones de Recuadros Clickeables */
    div[data-testid="stColumn"] button {
        width: 100% !important;
        height: 26px !important;
        min-height: 26px !important;
        padding: 0px !important;
        font-size: 0.75rem !important;
        font-weight: 900 !important;
        border-radius: 4px !important;
        margin: 0px !important;
        transition: all 0.15s ease-in-out;
    }
    
    /* Estado PENDIENTE (Gris Oscuro) */
    .btn-pending button {
        background-color: #1e293b !important;
        color: #64748b !important;
        border: 1px solid #334155 !important;
    }
    .btn-pending button:hover {
        background-color: #334155 !important;
        color: #ffffff !important;
        border-color: #38bdf8 !important;
    }
    
    /* Estado REALIZADO (Verde Brillante Visibilidad TV) */
    .btn-done button {
        background-color: #16a34a !important;
        color: #ffffff !important;
        border: 1px solid #22c55e !important;
        box-shadow: 0 0 8px rgba(34, 197, 94, 0.4) !important;
    }
    .btn-done button:hover {
        background-color: #15803d !important;
        border-color: #4ade80 !important;
    }
</style>
""",
    unsafe_allow_html=True,
)

# ---------------------------------------------------------
# NAVEGACIÓN
# ---------------------------------------------------------
st.sidebar.title('🎛️ NAVEGACIÓN')
modo = st.sidebar.radio(
    'Seleccionar Vista:', ['📱 Tablero TV Ejecutivo', '⚙️ Panel de Control']
)


# ---------------------------------------------------------
# TABLERO EJECUTIVO TV INTERACTIVO
# ---------------------------------------------------------
def renderizar_tablero_tv():
  hora_actual = datetime.now().strftime('%H:%M:%S')
  fecha_actual = datetime.now().strftime('%d/%m/%Y')

  # Header
  st.markdown(
      f"""
    <div class="tv-header">
        <div><span class="tv-badge">● EN VIVO</span> &nbsp;<span class="tv-title">CONTROL DE RECARGAS Y LOGÍSTICA</span></div>
        <div class="tv-time">⏱️ {hora_actual} <span style="font-size: 0.75rem; color: #94a3b8;">({fecha_actual})</span></div>
    </div>
    """,
      unsafe_allow_html=True,
  )

  # Leyenda
  legend_html = '<div class="legend-box">'
  for nombre, cfg in MOTORIZADOS_CONFIG.items():
    legend_html += f'<div class="legend-item"><span class="moto-badge" style="background-color: {cfg["bg"]}; color: {cfg["color"]};">{cfg["code"]}</span> {nombre}</div>'
  legend_html += '</div>'
  st.markdown(legend_html, unsafe_allow_html=True)

  df_maquinas = cargar_maquinas()
  total_registros = len(df_maquinas)

  # Dividir en 3 columnas paralelas
  num_cols = 3
  cols_st = st.columns(num_cols)
  chunk_size = (total_registros + num_cols - 1) // num_cols

  for i in range(num_cols):
    start_idx = i * chunk_size
    end_idx = min((i + 1) * chunk_size, total_registros)
    sub_df = df_maquinas.iloc[start_idx:end_idx]

    with cols_st[i]:
      # Encabezado de la columna
      h_loc, h_resp, h_l, h_m, h_x, h_j, h_v, h_s = st.columns(
          [0.36, 0.14, 0.08, 0.08, 0.08, 0.08, 0.08, 0.08]
      )
      h_loc.markdown(
          '<div class="table-header" style="text-align:left; padding-left:4px;">UBICACIÓN</div>',
          unsafe_allow_html=True,
      )
      h_resp.markdown(
          '<div class="table-header">RESP.</div>', unsafe_allow_html=True
      )
      h_l.markdown('<div class="table-header">L</div>', unsafe_allow_html=True)
      h_m.markdown('<div class="table-header">M</div>', unsafe_allow_html=True)
      h_x.markdown('<div class="table-header">X</div>', unsafe_allow_html=True)
      h_j.markdown('<div class="table-header">J</div>', unsafe_allow_html=True)
      h_v.markdown('<div class="table-header">V</div>', unsafe_allow_html=True)
      h_s.markdown('<div class="table-header">S</div>', unsafe_allow_html=True)

      # Filas estilizadas
      for _, row in sub_df.iterrows():
        m_id = row['id']
        c_loc, c_resp, c_l, c_m, c_x, c_j, c_v, c_s = st.columns(
            [0.36, 0.14, 0.08, 0.08, 0.08, 0.08, 0.08, 0.08]
        )

        cfg = MOTORIZADOS_CONFIG.get(
            row['motorizado'], MOTORIZADOS_CONFIG['Sin Asignar']
        )
        badge_html = f'<span class="moto-badge" style="background-color: {cfg["bg"]}; color: {cfg["color"]};">{cfg["code"]}</span>'

        c_loc.markdown(
            f'<div class="row-location" title="{row["nombre"]}">{row["nombre"]}</div>',
            unsafe_allow_html=True,
        )
        c_resp.markdown(
            f'<div style="text-align:center; padding-top:1px;">{badge_html}</div>',
            unsafe_allow_html=True,
        )

        # Matriz de recuadros interactivos (L, M, X, J, V, S)
        dias = [
            ('lunes', c_l),
            ('martes', c_m),
            ('miercoles', c_x),
            ('jueves', c_j),
            ('viernes', c_v),
            ('sabado', c_s),
        ]

        for dia_col, col_obj in dias:
          val_actual = int(row[dia_col])
          key_btn = f'btn_{m_id}_{dia_col}'

          # Si está marcado, verde brillante con ✓. Si no, recuadro oscuro.
          label_str = '✓' if val_actual == 1 else '·'
          css_class = 'btn-done' if val_actual == 1 else 'btn-pending'

          with col_obj:
            st.markdown(f'<div class="{css_class}">', unsafe_allow_html=True)
            if st.button(label_str, key=key_btn):
              toggle_dia_db(m_id, dia_col, val_actual)
              st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)


# ---------------------------------------------------------
# PANEL DE ADMINISTRACIÓN
# ---------------------------------------------------------
if modo == '📱 Tablero TV Ejecutivo':
  renderizar_tablero_tv()

elif modo == '⚙️ Panel de Control':
  st.title('⚙️ Panel de Gestión de Máquinas')
  st.markdown('---')

  pin_ingresado = st.sidebar.text_input(
      'Clave Supervisor:', type='password', value='1234'
  )

  if pin_ingresado != '1234':
    st.warning('🔒 Ingrese la clave de supervisor para gestionar datos.')
  else:
    st.success('🔓 Acceso concedido.')

    if st.sidebar.button('🔄 Restablecer 61 Ubicaciones Maestras'):
      with st.spinner('⏳ Restableciendo lista...'):
        time.sleep(0.3)
        init_db(force_reset=True)
      st.sidebar.success('¡Base de datos restablecida!')
      st.rerun()

    col_form, col_tabla = st.columns([1, 2])

    with col_form:
      st.subheader('➕ Agregar Ubicación')
      with st.form('form_agregar', clear_on_submit=True):
        nombre_nuevo = st.text_input('Nombre de Ubicación:')
        moto_nuevo = st.selectbox(
            'Motorizado Asignado:', MOTORIZADOS_DISPONIBLES, index=0
        )

        st.write('**Días de Recarga Iniciales:**')
        c_l, c_m, c_x, c_j, c_v, c_s = st.columns(6)
        l_val = c_l.checkbox('L', value=False)
        m_val = c_m.checkbox('M', value=False)
        x_val = c_x.checkbox('X', value=False)
        j_val = c_j.checkbox('J', value=False)
        v_val = c_v.checkbox('V', value=False)
        s_val = c_s.checkbox('S', value=False)

        btn_guardar = st.form_submit_button('💾 Guardar Ubicación')

        if btn_guardar:
          if nombre_nuevo.strip():
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
            st.success(f"Ubicación '{nombre_nuevo}' guardada.")
            st.rerun()
          else:
            st.error('El nombre no puede estar vacío.')

    with col_tabla:
      st.subheader('📋 Edición de Asignaciones')
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
              eliminar_maquina(row['id'])
              st.warning('Registro eliminado.')
              st.rerun()