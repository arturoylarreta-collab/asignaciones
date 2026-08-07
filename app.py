"""
Sistema de Control Logístico y Distribución en Streamlit
Diseñado para Pantalla TV 43" (Vista Matriz Estilo Pizarra)
"""

import os
import sqlite3
import tempfile
from datetime import datetime
import pandas as pd
import streamlit as st

# ---------------------------------------------------------
# CONFIGURACIÓN DE PÁGINA (Layout Ancho para TV)
# ---------------------------------------------------------
st.set_page_config(
    page_title='Tablero Logístico - TV 43"',
    page_icon='🚚',
    layout='wide',
    initial_sidebar_state='collapsed',
)

DB_NAME = os.path.join(tempfile.gettempdir(), 'logistica_streamlit.db')


# ---------------------------------------------------------
# BASE DE DATOS SQLITE
# ---------------------------------------------------------
def get_db_connection():
  conn = sqlite3.connect(DB_NAME, check_same_thread=False)
  conn.row_factory = sqlite3.Row
  return conn


def init_db():
  conn = get_db_connection()
  cursor = conn.cursor()
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS maquinas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            prioridad TEXT NOT NULL,
            motorizado TEXT DEFAULT 'Sin Asignar',
            lunes INTEGER DEFAULT 1,
            martes INTEGER DEFAULT 1,
            miercoles INTEGER DEFAULT 1,
            jueves INTEGER DEFAULT 1,
            viernes INTEGER DEFAULT 1,
            sabado INTEGER DEFAULT 0,
            observaciones TEXT DEFAULT ''
        )
    """)

  cursor.execute('SELECT COUNT(*) FROM maquinas')
  if cursor.fetchone()[0] == 0:
    sample_data = [
        (
            'Provincial Call Center',
            'ALTA',
            'Carlos Mendoza',
            1,
            0,
            0,
            0,
            0,
            0,
            'Ruta centro',
        ),
        (
            'Robin',
            'MEDIA',
            'Roberto Gómez',
            1,
            0,
            1,
            0,
            0,
            0,
            'Zona norte',
        ),
        (
            'UCAB Labs - M3',
            'ALTA',
            'Juan Pérez',
            0,
            1,
            0,
            0,
            0,
            0,
            'Prioridad VIP',
        ),
        (
            'Bangente Cubo Negro',
            'ALTA',
            'Carlos Mendoza',
            1,
            0,
            1,
            0,
            0,
            0,
            'Ruta este',
        ),
        (
            'Cashea Piso 9 y 18',
            'MEDIA',
            'Roberto Gómez',
            0,
            0,
            1,
            0,
            1,
            0,
            'Atención continua',
        ),
        (
            'Sanatrix',
            'BAJA',
            'Sin Asignar',
            1,
            0,
            0,
            1,
            0,
            0,
            'Mantenimiento',
        ),
        (
            'Venemergencia Chacao',
            'ALTA',
            'Juan Pérez',
            1,
            0,
            0,
            1,
            0,
            0,
            'Urgente',
        ),
    ]
    cursor.executemany(
        """
            INSERT INTO maquinas (nombre, prioridad, motorizado, lunes, martes, miercoles, jueves, viernes, sabado, observaciones)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        sample_data,
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
    prioridad,
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
        INSERT INTO maquinas (nombre, prioridad, motorizado, lunes, martes, miercoles, jueves, viernes, sabado)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
      (
          nombre,
          prioridad,
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
    prioridad,
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
        UPDATE maquinas SET nombre=?, prioridad=?, motorizado=?, lunes=?, martes=?, miercoles=?, jueves=?, viernes=?, sabado=?
        WHERE id=?
    """,
      (
          nombre,
          prioridad,
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
# ESTILOS CSS PERSONALIZADOS (ESTILO PIZARRA DE CONTROL)
# ---------------------------------------------------------
st.markdown(
    """
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stApp { background-color: #0f172a; color: #f8fafc; }
    
    .tv-container {
        width: 100%;
        background-color: #1e293b;
        border-radius: 12px;
        padding: 10px;
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
        font-size: 1.4rem;
        font-weight: 800;
        text-transform: uppercase;
        padding: 1.1rem;
        border-bottom: 3px solid #334155;
        text-align: left;
    }
    .tv-table th.day-header {
        text-align: center;
        width: 7%;
        font-size: 1.5rem;
        color: #f8fafc;
    }
    .tv-table td {
        padding: 1rem;
        border-bottom: 1px solid #334155;
        font-size: 1.35rem;
        font-weight: 600;
        vertical-align: middle;
    }
    .tv-table tr:nth-child(even) { background-color: #1a2436; }
    
    .prio-badge {
        display: inline-block;
        padding: 0.4rem 0.8rem;
        border-radius: 8px;
        font-weight: 800;
        font-size: 1.1rem;
        text-align: center;
        width: 100%;
    }
    .prio-ALTA { background-color: #dc2626; color: #ffffff; }
    .prio-MEDIA { background-color: #d97706; color: #ffffff; }
    .prio-BAJA { background-color: #16a34a; color: #ffffff; }
    .prio-MANTENIMIENTO { background-color: #475569; color: #cbd5e1; }
    
    .day-pill {
        display: inline-flex;
        width: 42px;
        height: 42px;
        align-items: center;
        justify-content: center;
        border-radius: 8px;
        font-weight: 800;
        font-size: 1.2rem;
        background-color: #0284c7;
        color: #ffffff;
        box-shadow: 0 0 10px rgba(2, 132, 199, 0.6);
    }
    .day-pill-sat {
        background-color: #7c3aed;
        box-shadow: 0 0 10px rgba(124, 58, 237, 0.6);
    }
    .day-empty {
        color: #475569;
        font-weight: 400;
        font-size: 1.4rem;
    }
    
    .live-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background-color: #1e293b;
        padding: 1rem 1.5rem;
        border-radius: 12px;
        margin-bottom: 1rem;
        border: 1px solid #334155;
    }
    .live-badge {
        background-color: #ef4444;
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-weight: bold;
        font-size: 1.1rem;
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
refresco_sec = st.sidebar.slider(
    'Frecuencia de Auto-refresco TV (segundos):', 3, 30, 5
)

if modo == '📺 Tablero TV 43"':
  st.markdown(
      f'<meta http-equiv="refresh" content="{refresco_sec}">',
      unsafe_allow_html=True,
  )

  hora_actual = datetime.now().strftime('%H:%M:%S')
  fecha_actual = datetime.now().strftime('%d/%m/%Y')

  col_h1, col_h2 = st.columns([3, 1])
  with col_h1:
    st.markdown(
        f"""
        <div class="live-header">
            <div>
                <span class="live-badge">● EN VIVO</span>
                <span style="font-size: 1.8rem; font-weight: 800; margin-left: 10px; color: #f1f5f9;">PROGRAMACIÓN SEMANAL DE RECARGA</span>
            </div>
            <div style="font-size: 1.8rem; font-weight: 700; color: #38bdf8;">
                ⏱️ {hora_actual} <span style="font-size: 1.1rem; color: #94a3b8;">({fecha_actual})</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

  df_maquinas = cargar_maquinas()

  def get_cell(active, code, is_sat=False):
    if active:
      cls = 'day-pill day-pill-sat' if is_sat else 'day-pill'
      return f'<span class="{cls}">✓ {code}</span>'
    return '<span class="day-empty">-</span>'

  html_rows = ''
  for _, m in df_maquinas.iterrows():
    c_l = get_cell(m['lunes'], 'L')
    c_m = get_cell(m['martes'], 'M')
    c_x = get_cell(m['miercoles'], 'X')
    c_j = get_cell(m['jueves'], 'J')
    c_v = get_cell(m['viernes'], 'V')
    c_s = get_cell(m['sabado'], 'S', is_sat=True)

    html_rows += f'<tr><td style="font-weight: 800; color: #ffffff;">{m["nombre"]}</td><td><span class="prio-badge prio-{m["prioridad"]}">{m["prioridad"]}</span></td><td>🛵 <span style="color: #f1f5f9; font-weight: 700;">{m["motorizado"]}</span></td><td style="text-align: center;">{c_l}</td><td style="text-align: center;">{c_m}</td><td style="text-align: center;">{c_x}</td><td style="text-align: center;">{c_j}</td><td style="text-align: center;">{c_v}</td><td style="text-align: center;">{c_s}</td></tr>'

  tabla_completa = f'<div class="tv-container"><table class="tv-table"><thead><tr><th style="width: 30%;">Máquina / Ubicación</th><th style="width: 14%;">Prioridad</th><th style="width: 22%;">Motorizado Asignado</th><th class="day-header">L</th><th class="day-header">M</th><th class="day-header">X</th><th class="day-header">J</th><th class="day-header">V</th><th class="day-header">S</th></tr></thead><tbody>{html_rows}</tbody></table></div>'

  st.markdown(tabla_completa, unsafe_allow_html=True)

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

    col_form, col_tabla = st.columns([1, 2])

    with col_form:
      st.subheader('➕ Agregar Nueva Máquina')
      with st.form('form_agregar', clear_on_submit=True):
        nombre_nuevo = st.text_input('Máquina / Ubicación:')
        prio_nueva = st.selectbox(
            'Prioridad:', ['ALTA', 'MEDIA', 'BAJA', 'MANTENIMIENTO'], index=1
        )
        moto_nuevo = st.text_input(
            'Motorizado Asignado:', value='Sin Asignar'
        )

        st.write('**Días de Recarga:**')
        c_l, c_m, c_x, c_j, c_v, c_s = st.columns(6)
        l_val = c_l.checkbox('L', value=True)
        m_val = c_m.checkbox('M', value=False)
        x_val = c_x.checkbox('X', value=False)
        j_val = c_j.checkbox('J', value=False)
        v_val = c_v.checkbox('V', value=False)
        s_val = c_s.checkbox('S', value=False)

        btn_guardar = st.form_submit_button('💾 Guardar Máquina')
        if btn_guardar:
          if nombre_nuevo.strip():
            agregar_maquina(
                nombre_nuevo,
                prio_nueva,
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
            f"📌 {row['nombre']} — Prioridad: {row['prioridad']} | Motorizado:"
            f" {row['motorizado']}"
        ):
          with st.form(f"form_edit_{row['id']}"):
            e_nombre = st.text_input('Ubicación:', value=row['nombre'])
            e_prio = st.selectbox(
                'Prioridad:',
                ['ALTA', 'MEDIA', 'BAJA', 'MANTENIMIENTO'],
                index=[
                    'ALTA',
                    'MEDIA',
                    'BAJA',
                    'MANTENIMIENTO',
                ].index(row['prioridad']),
            )
            e_moto = st.text_input('Motorizado:', value=row['motorizado'])

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
                  e_prio,
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