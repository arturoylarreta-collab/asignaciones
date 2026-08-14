import os
import sqlite3
from datetime import datetime
import pandas as pd

DB_PATH = "vendu_logistica.db"
UPLOADS_DIR = "uploads"


def init_db():
    """Crea la tabla en SQLite si no existe y la carpeta de imágenes."""
    os.makedirs(UPLOADS_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS registro_visitas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha_hora DATETIME DEFAULT CURRENT_TIMESTAMP,
            motorizado TEXT NOT NULL,
            punto_nombre TEXT NOT NULL,
            estado_carga TEXT CHECK(estado_carga IN ('PENDIENTE', 'EN RUTA', 'FINALIZADO')),
            duracion_minutos INTEGER DEFAULT 0,
            foto_limpia_path TEXT,
            foto_rellena_path TEXT,
            observaciones TEXT
        )
    """)
    conn.commit()
    conn.close()


def guardar_visita(motorizado, punto, estado, foto_limpia, foto_rellena, observaciones, duracion):
    """Guarda las fotos localmente y el registro en SQLite."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path_limpia = None
    path_rellena = None

    # Guardar Foto Limpia
    if foto_limpia:
        filename_l = f"{punto}_{timestamp}_limpia.jpg".replace(" ", "_")
        path_limpia = os.path.join(UPLOADS_DIR, filename_l)
        with open(path_limpia, "wb") as f:
            f.write(foto_limpia.getbuffer())

    # Guardar Foto Rellena
    if foto_rellena:
        filename_r = f"{punto}_{timestamp}_rellena.jpg".replace(" ", "_")
        path_rellena = os.path.join(UPLOADS_DIR, filename_r)
        with open(path_rellena, "wb") as f:
            f.write(foto_rellena.getbuffer())

    cursor.execute("""
        INSERT INTO registro_visitas 
        (motorizado, punto_nombre, estado_carga, duracion_minutos, foto_limpia_path, foto_rellena_path, observaciones)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (motorizado, punto, estado, duracion, path_limpia, path_rellena, observaciones))

    conn.commit()
    conn.close()


def obtener_visitas_df():
    """Obtiene todo el historial registrado en la base de datos."""
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM registro_visitas ORDER BY fecha_hora DESC", conn)
    conn.close()
    return df