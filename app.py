"""
Sistema de Control Logístico y Distribución en Streamlit
Diseñado para Pantalla TV 43" (Vista Compacta - 36 filas en 1 sola pantalla)
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
    page_title='Tablero Logístico - TV 43"',
    page_icon='🚚',
    layout='wide',
    initial_sidebar_state='expanded',  # Ahora la barra lateral inicia ABIERTA
)

DB_NAME = os.path.join(tempfile.gettempdir(), 'logistica_streamlit.db')

MOTORIZADOS_DISPONIBLES = [
    'Eduard',
    'Freduard',
    'Alejandro',
    'Gustavo',
    'Sin Asignar',
]


# ---------------------------------------------------------
# BASE DE DATOS SQLITE (AUTO-RESETEO SI HAY DATOS VIEJOS)
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

  # Si detecta los datos de prueba viejos ("Embaladora"), los borra y carga la lista real de 36
  cursor.execute(
      "SELECT COUNT(*) FROM maquinas WHERE nombre LIKE '%Embaladora%'"
  )
  hay_datos_viejos = cursor.fetchone()[0] > 0

  cursor.execute('SELECT COUNT(*) FROM maquinas')
  total_registros = cursor.fetchone()[0]

  if hay_datos_viejos or total_registros == 0:
    cursor.execute('DELETE FROM maquinas')

    sample_locations = [
        ('Unimet PB', 'Eduard', 1, 0, 1, 0, 0, 0),
        ('Unimet LAB', 'Eduard', 0, 1, 0, 1, 0, 0),
        ('Unimet EM', 'Eduard', 1, 0, 0, 0, 1, 0),
        ('UCAB CONVERT', 'Freduard', 0, 0, 1, 1, 0, 0),
        ('UCAB LAB', 'Freduard', 0, 1, 0, 0, 1, 0),
        ('UCAB P1', 'Freduard', 1, 0, 0, 0, 0, 0),
        ('UCAB MEZ', 'Freduard', 0, 1, 0, 0, 0, 0),
        ('UCAB M3', 'Freduard', 0, 0, 1, 0, 0, 0),
        ('USM', 'Alejandro', 1, 0, 1, 0, 1, 0),
        ('MONTAÑA', 'Alejandro', 0, 0, 0, 1, 0, 0),
        ('EURO S1', 'Gustavo', 1, 0, 0, 1, 0, 0),
        ('EURO S2', 'Gustavo', 0, 1, 0, 0, 1, 0),
        ('TAMACO', 'Eduard', 0, 1, 0, 0, 0, 0),
        ('TAMACA', 'Eduard', 0, 1, 0, 0, 0, 0),
        ('HUMBOLDT', 'Alejandro', 1, 0, 0, 0, 0, 0),
        ('GOLD DATA', 'Gustavo', 0, 0, 1, 0, 0, 0),
        ('PAGO DIRECTO', 'Gustavo', 1, 0, 1, 0, 1, 0),
        ('CUBITT', 'Alejandro', 0, 1, 0, 1, 0, 0),
        ('KURIOS', 'Eduard', 0, 0, 0, 0, 1, 0),
        ('CASHEA P9', 'Freduard', 1, 0, 1, 0, 1, 0),
        ('CASHEA P18', 'Freduard', 1, 0, 1, 0, 1, 0),
        ('DICAM', 'Alejandro', 0, 1, 0, 0, 0, 0),
        ('FISA', 'Gustavo', 0, 0, 1, 0, 0, 0),
        ('DOMESA', 'Eduard', 1, 1, 1, 1, 1, 0),
        ('TU GRUERO', 'Alejandro', 0, 0, 0, 1, 0, 0),
        ('UNION RADIO', 'Gustavo', 1, 0, 0, 1, 0, 0),
        ('FORUM P7', 'Freduard', 0, 1, 0, 0, 1, 0),
        ('FORUM P15', 'Freduard', 0, 1, 0, 0, 1, 0),
        ('BANGENTE', 'Alejandro', 1, 0, 1, 0, 0, 0),
        ('PROVINCIAL', 'Gustavo', 1, 0, 0, 0, 0, 0),
        ('TRANRED', 'Eduard', 0, 0, 1, 0, 0, 0),
        ('ROBIN', 'Alejandro', 1, 0, 1, 0, 0, 0),
        ('CALLCENTER DRCC', 'Gustavo', 1, 0, 0, 0, 0, 0),
        ('DUNCAN', 'Eduard', 0, 0, 0, 1, 0, 0),
        ('PEGASO', 'Alejandro', 0, 1, 0, 0, 0, 0),
        ('ASIMETRIX', 'Freduard', 1, 0, 0, 0, 0, 0),
    ]

    cursor.executemany(
        """
            INSERT INTO maquinas (nombre, motorizado, lunes, martes, miercoles, jueves, viernes, sabado)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
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
    nombre,
    motorizado,
    lunes,
    martes,
    miercoles,
    jueves,
    viernes,
    sabado,
):
  conn = get_db_connection()
  cursor = conn.cursor()
  cursor.execute(
      """
        INSERT INTO maquinas (nombre, motorizado, lunes, martes, miercoles, jueves, viernes, sabado)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
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
    m_id,
    nombre,
    motorizado,
    lunes,
    martes,
    miercoles,
    jueves,
    viernes,
    sabado,
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
# ESTILOS CSS (BOTÓN DE MENÚ SIEMPRE VISIBLE)
# ---------------------------------------------------------
st.markdown(
    """
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Mantiene visible únicamente el botón del menú lateral */
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
        padding-top: 2rem !important;
        padding-bottom: 0.2rem !important;
        padding-left: 0.8rem !important;
        padding-right: 0.8rem !important;
        max-width: 100% !important;
    }
    
    .stApp { background-color: #0f172a; color: #f8fafc; }
    
    .tv-container {
        width: 100%;
        background-color: #1e293b;
        border-radius: 8px;
        padding: 4px;
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
        font-size: 0.95rem;
        font-weight: 800;
        text-transform: uppercase;
        padding: 0.3rem 0.5rem;
        border-bottom: 2px solid #334155;
        text-align: left;
    }
    .tv-table th.day-header {
        text-align: center;
        width: 6%;
        font-size: 1rem;
        color: #f8fafc;
    }
    .tv-table td {
        padding: 0.15rem 0.5rem !important;
        border-bottom: 1px solid #334155;
        font-size: 0.85rem;
        font-weight: 700;
        vertical-align: middle;
        line-height: 1.1;
    }
    .tv-table tr:nth-child(even) { background-color: #1a2436; }
    
    .day-pill {
        display: inline-flex;
        width: 22px;
        height: 22px;
        align-items: center;
        justify-content: center;
        border-radius: 4px;
        font-weight: 800;
        font-size: 0.75rem;
        background-color: #0284c7;
        color: #ffffff;
    }
    .day-pill-sat { background-color: #7c3aed; }
    .day-empty { color: #475569; font-weight: 400; font-size: 0.85rem; }
    
    .live-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background-color: #1e293b;
        padding: 0.4rem 1rem;
        border-radius: 8px;
        margin-bottom: 0.4rem;
        border: 1px solid #334155;
    }
    .live-badge {
        background-color: #ef4444;
        color: white;
        padding: 0.15rem 0.5rem;
        border-radius: 12px;
        font-weight: bold;
        font-size: 0.85rem;
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
    'Seleccionar Vista:', ['📺 Tablero TV 43"', '⚙️ Panel de Control (Jefes)']
)


# ---------------------------------------------------------
# TABLERO TV EN VIVO
# ---------------------------------------------------------
@st.fragment(run_every=10)
def renderizar_tablero_tv():
  hora_actual = datetime.now().strftime('%H:%M:%S')
  fecha_actual = datetime.now().strftime('%d/%m/%Y')

  st.markdown(
      f"""
    <div class="live-header">
        <div>
            <span class="live-badge">● EN VIVO</span>
            <span style="font-size: 1.2rem; font-weight: 800; margin-left: 8px; color: #f1f5f9;">PROGRAMACIÓN SEMANAL DE RECARGA</span>
        </div>
        <div style="font-size: 1.2rem; font-weight: 700; color: #38bdf8;">
            ⏱️ {hora_actual} <span style="font-size: 0.9rem; color: #94a3b8;">({fecha_actual})</span>
        </div>
    </div>
    """,
      unsafe_allow_html=True,
  )

  df_maquinas = cargar_maquinas()

  def get_cell(active, is_sat=False):
    if active:
      cls = 'day-pill day-pill-sat' if is_sat else 'day-pill'
      return f'<span class="{cls}">✓</span>'
    return '<span class="day-empty">-</span>'

  html_rows = ''
  for _, m in df_maquinas.iterrows():
    c_l = get_cell(m['lunes'])
    c_m = get_cell(m['martes'])
    c_x = get_cell(m['miercoles'])
    c_j = get_cell(m['jueves'])
    c_v = get_cell(m['viernes'])
    c_s = get_cell(m['sabado'], is_sat=True)

    html_rows += f'<tr><td style="font-weight: 800; color: #ffffff;">{m["nombre"]}</td><td>🛵 <span style="color: #f1f5f9; font-weight: 700;">{m["motorizado"]}</span></td><td style="text-align: center;">{c_l}</td><td style="text-align: center;">{c_m}</td><td style="text-align: center;">{c_x}</td><td style="text-align: center;">{c_j}</td><td style="text-align: center;">{c_v}</td><td style="text-align: center;">{c_s}</td></tr>'

  tabla_completa = f'<div class="tv-container"><table class="tv-table"><thead><tr><th style="width: 44%;">MÁQUINA / UBICACIÓN</th><th style="width: 20%;">MOTORIZADO ASIGNADO</th><th class="day-header">L</th><th class="day-header">M</th><th class="day-header">X</th><th class="day-header">J</th><th class="day-header">V</th><th class="day-header">S</th></tr></thead><tbody>{html_rows}</tbody></table></div>'

  st.markdown(tabla_completa, unsafe_allow_html=True)


# ---------------------------------------------------------
# VISTAS
# ---------------------------------------------------------
if modo == '📺 Tablero TV 43"':
  renderizar_tablero_tv()

elif modo == '⚙️ Panel de Control (Jefes)':
  st.title('⚙️ Panel de Gestión de Máquinas y Motorizados')
  st.markdown('---')

  pin_ingresado = st.sidebar.text_input(
      'Clave de Acceso Supervisor:', type='password', value='1234'
  )

  if pin_ingresado != '1234':
    st.warning('🔒 Ingrese la clave de supervisor correcta para editar.')
  else:
    st.success('🔓 Acceso concedido como Supervisor.')

    if st.sidebar.button('🔄 Recargar/Restablecer Lista Base'):
      init_db(force_reset=True)
      st.sidebar.success('¡Base de datos restablecida!')
      st.rerun()

    col_form, col_tabla = st.columns([1, 2])

    with col_form:
      st.subheader('➕ Agregar Nueva Ubicación')
      with st.form('form_agregar', clear_on_submit=True):
        nombre_nuevo = st.text_input('Máquina / Ubicación:')
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
            st.success(f"Ubicación '{nombre_nuevo}' agregada con éxito.")
            st.rerun()
          else:
            st.error('El nombre de la ubicación no puede estar vacío.')

    with col_tabla:
      st.subheader('📋 Modificar / Asignar Existentes')
      df = cargar_maquinas()

      for index, row in df.iterrows():
        with st.expander(
            f"📌 {row['nombre']} | Motorizado: {row['motorizado']}"
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

            st.write('**Días Activos de Recarga:**')
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
              btn_actualizar = st.form_submit_button('💾 Actualizar Cambios')
            with col_b2:
              btn_eliminar = st.form_submit_button('🗑️ Eliminar Registro')

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