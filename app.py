"""
Sistema de Control Logístico y Distribución - Tablero TV 43" & Panel de Control
Desarrollado en Python con Flask + SQLite
"""

import sqlite3
from flask import Flask, render_template_string, request, jsonify, redirect, url_for

app = Flask(__name__)
DB_NAME = "logistica.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS maquinas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            prioridad TEXT NOT NULL, -- ALTA, MEDIA, BAJA, MANTENIMIENTO
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
    
    # Insert initial sample data if empty
    cursor.execute("SELECT COUNT(*) FROM maquinas")
    if cursor.fetchone()[0] == 0:
        sample_data = [
            ("Máquina Embaladora 01", "ALTA", "Carlos Mendoza", 1, 1, 1, 1, 1, 1, "Envíos expresos ciudad"),
            ("Inyectora Plásticos M-02", "MEDIA", "Roberto Gómez", 1, 1, 1, 1, 1, 0, "Ruta Zona Norte"),
            ("Sopladora PET 03", "BAJA", "Sin Asignar", 1, 0, 1, 0, 1, 0, "Mantenimiento preventivo"),
            ("Línea de Envasado 04", "ALTA", "Juan Pérez", 1, 1, 1, 1, 1, 1, "Prioridad clientes VIP"),
            ("Selladora Industrial 05", "MANTENIMIENTO", "N/A", 0, 0, 0, 0, 0, 0, "En revisión técnica")
        ]
        cursor.executemany("""
            INSERT INTO maquinas (nombre, prioridad, motorizado, lunes, martes, miercoles, jueves, viernes, sabado, observaciones)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, sample_data)
        conn.commit()
    conn.close()

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

# ---------------------------------------------------------
# PLANTILLAS HTML EMBEBIDAS (Optimizado para TV 43" & Admin)
# ---------------------------------------------------------

TV_HTML = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TABLERO LOGÍSTICO - TV 43"</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; }
        body { background-color: #0f172a; color: #f8fafc; overflow: hidden; height: 100vh; padding: 1.5rem; }
        
        /* Header */
        .header { display: flex; justify-content: space-between; align-items: center; padding-bottom: 1rem; border-bottom: 2px solid #334155; margin-bottom: 1.2rem; }
        .title-box { display: flex; align-items: center; gap: 1rem; }
        .badge-live { background-color: #ef4444; color: white; padding: 0.3rem 0.8rem; border-radius: 20px; font-weight: bold; font-size: 1rem; animation: pulse 2s infinite; }
        .title { font-size: 2rem; font-weight: 800; letter-spacing: 1px; color: #f1f5f9; }
        .clock { font-size: 2.2rem; font-weight: 700; color: #38bdf8; font-mono: monospace; }
        
        /* Table / Grid */
        .table-container { width: 100%; height: calc(100vh - 120px); overflow: hidden; background: #1e293b; border-radius: 12px; border: 1px solid #334155; box-shadow: 0 10px 25px rgba(0,0,0,0.5); }
        table { width: 100%; border-collapse: collapse; text-align: left; table-layout: fixed; }
        th { background-color: #0f172a; color: #94a3b8; font-size: 1.25rem; font-weight: 700; text-transform: uppercase; padding: 1.2rem 1rem; border-bottom: 2px solid #334155; }
        td { padding: 1.1rem 1rem; border-bottom: 1px solid #334155; font-size: 1.35rem; font-weight: 600; vertical-align: middle; }
        tr:nth-child(even) { background-color: #1a2436; }
        
        /* Priority Badges */
        .prio-tag { padding: 0.6rem 1.2rem; border-radius: 8px; font-weight: 800; font-size: 1.2rem; display: inline-block; text-align: center; width: 100%; box-shadow: 0 2px 4px rgba(0,0,0,0.2); }
        .prio-ALTA { background-color: #dc2626; color: #ffffff; }
        .prio-MEDIA { background-color: #d97706; color: #ffffff; }
        .prio-BAJA { background-color: #16a34a; color: #ffffff; }
        .prio-MANTENIMIENTO { background-color: #475569; color: #cbd5e1; }
        
        /* Days Badges */
        .days-container { display: flex; gap: 0.4rem; justify-content: center; }
        .day-box { width: 38px; height: 38px; border-radius: 6px; display: flex; align-items: center; justify-content: center; font-size: 1.1rem; font-weight: bold; background: #334155; color: #64748b; }
        .day-active { background: #0284c7; color: #ffffff; box-shadow: 0 0 8px rgba(2, 132, 199, 0.5); }
        .day-sat { background: #7c3aed; color: #ffffff; }
        
        /* Motorizado */
        .driver-box { display: flex; align-items: center; gap: 0.5rem; color: #f3f4f6; }
        .driver-icon { font-size: 1.5rem; }
        
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.4; }
            100% { opacity: 1; }
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="title-box">
            <span class="badge-live">● EN VIVO</span>
            <span class="title">CONTROL DE DISTRIBUCIÓN Y MÁQUINAS</span>
        </div>
        <div class="clock" id="clock">00:00:00</div>
    </div>

    <div class="table-container">
        <table>
            <thead>
                <tr>
                    <th style="width: 28%;">Máquina / Equipo</th>
                    <th style="width: 16%;">Prioridad</th>
                    <th style="width: 24%;">Motorizado Asignado</th>
                    <th style="width: 22%; text-align: center;">Días Laborales</th>
                    <th style="width: 10%; text-align: center;">Sábado</th>
                </tr>
            </thead>
            <tbody id="table-body">
                <!-- Se llena dinámicamente vía AJAX -->
            </tbody>
        </table>
    </div>

    <script>
        function updateClock() {
            const now = new Date();
            document.getElementById('clock').innerText = now.toLocaleTimeString('es-ES', { hour12: false });
        }
        setInterval(updateClock, 1000);
        updateClock();

        function loadData() {
            fetch('/api/maquinas')
                .then(response => response.json())
                .then(data => {
                    const tbody = document.getElementById('table-body');
                    tbody.innerHTML = '';
                    data.forEach(m => {
                        const tr = document.createElement('tr');
                        tr.innerHTML = `
                            <td style="font-weight: 700; color: #f8fafc;">${m.nombre}</td>
                            <td><span class="prio-tag prio-${m.prioridad}">${m.prioridad}</span></td>
                            <td>
                                <div class="driver-box">
                                    <span class="driver-icon">🛵</span>
                                    <span>${m.motorizado}</span>
                                </div>
                            </td>
                            <td>
                                <div class="days-container">
                                    <div class="day-box ${m.lunes ? 'day-active' : ''}">L</div>
                                    <div class="day-box ${m.martes ? 'day-active' : ''}">M</div>
                                    <div class="day-box ${m.miercoles ? 'day-active' : ''}">X</div>
                                    <div class="day-box ${m.jueves ? 'day-active' : ''}">J</div>
                                    <div class="day-box ${m.viernes ? 'day-active' : ''}">V</div>
                                </div>
                            </td>
                            <td>
                                <div class="days-container">
                                    <div class="day-box ${m.sabado ? 'day-sat' : ''}">S</div>
                                </div>
                            </td>
                        `;
                        tbody.appendChild(tr);
                    });
                });
        }

        // Auto-refresco continuo sin parpadear la pantalla
        setInterval(loadData, 3000);
        loadData();
    </script>
</body>
</html>
"""

ADMIN_HTML = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Panel de Control Jefes - Gestión de Logística</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background-color: #f8fafc; color: #1e293b; padding-bottom: 3rem; }
        .navbar { background-color: #0f172a; }
        .card { border-radius: 12px; border: none; box-shadow: 0 4px 12px rgba(0,0,0,0.05); }
        .table th { background-color: #e2e8f0; }
        .badge-ALTA { background-color: #dc2626; color: white; }
        .badge-MEDIA { background-color: #d97706; color: white; }
        .badge-BAJA { background-color: #16a34a; color: white; }
        .badge-MANTENIMIENTO { background-color: #64748b; color: white; }
    </style>
</head>
<body>
    <nav class="navbar navbar-dark mb-4">
        <div class="container-fluid px-4">
            <a class="navbar-brand fw-bold" href="#">⚙️ PANEL DE GESTIÓN LOGÍSTICA (SUPERVISORES)</a>
            <a href="/" target="_blank" class="btn btn-outline-light btn-sm">📺 Ver Pantalla TV</a>
        </div>
    </nav>

    <div class="container-fluid px-4">
        <div class="row g-4">
            <!-- Formulario Nueva Máquina -->
            <div class="col-lg-4">
                <div class="card p-4">
                    <h5 class="fw-bold mb-3">➕ Registrar Nueva Máquina</h5>
                    <form action="/admin/agregar" method="POST">
                        <div class="mb-3">
                            <label class="form-label font-weight-bold">Nombre / Descripción de Máquina</label>
                            <input type="text" name="nombre" class="form-control" required placeholder="Ej: Empacadora Línea 3">
                        </div>
                        <div class="mb-3">
                            <label class="form-label font-weight-bold">Prioridad</label>
                            <select name="prioridad" class="form-select">
                                <option value="ALTA">🔴 ALTA (Urgente)</option>
                                <option value="MEDIA" selected>🟡 MEDIA (Normal)</option>
                                <option value="BAJA">🟢 BAJA (Disponible)</option>
                                <option value="MANTENIMIENTO">⚪ EN MANTENIMIENTO</option>
                            </select>
                        </div>
                        <div class="mb-3">
                            <label class="form-label font-weight-bold">Motorizado Asignado</label>
                            <input type="text" name="motorizado" class="form-control" placeholder="Ej: Juan Pérez">
                        </div>
                        <div class="mb-3">
                            <label class="form-label font-weight-bold">Días de Operación</label>
                            <div class="d-flex flex-wrap gap-2">
                                <div class="form-check"><input class="form-check-input" type="checkbox" name="lunes" checked><label class="form-check-label">Lun</label></div>
                                <div class="form-check"><input class="form-check-input" type="checkbox" name="martes" checked><label class="form-check-label">Mar</label></div>
                                <div class="form-check"><input class="form-check-input" type="checkbox" name="miercoles" checked><label class="form-check-label">Mié</label></div>
                                <div class="form-check"><input class="form-check-input" type="checkbox" name="jueves" checked><label class="form-check-label">Jue</label></div>
                                <div class="form-check"><input class="form-check-input" type="checkbox" name="viernes" checked><label class="form-check-label">Vie</label></div>
                                <div class="form-check ms-2 border-start ps-2"><input class="form-check-input" type="checkbox" name="sabado"><label class="form-check-label fw-bold text-primary">Sáb</label></div>
                            </div>
                        </div>
                        <button type="submit" class="btn btn-primary w-100 fw-bold">Guardar Máquina</button>
                    </form>
                </div>
            </div>

            <!-- Lista para Edición Rápida -->
            <div class="col-lg-8">
                <div class="card p-4">
                    <h5 class="fw-bold mb-3">📋 Estado Actual y Asignaciones</h5>
                    <div class="table-responsive">
                        <table class="table table-hover align-middle">
                            <thead>
                                <tr>
                                    <th>Máquina</th>
                                    <th>Prioridad</th>
                                    <th>Motorizado</th>
                                    <th>Días Activos</th>
                                    <th>Acciones</th>
                                </tr>
                            </thead>
                            <tbody>
                                {% for m in maquinas %}
                                <tr>
                                    <form action="/admin/editar/{{ m.id }}" method="POST">
                                        <td>
                                            <input type="text" name="nombre" value="{{ m.nombre }}" class="form-control form-control-sm fw-bold">
                                        </td>
                                        <td>
                                            <select name="prioridad" class="form-select form-select-sm">
                                                <option value="ALTA" {% if m.prioridad == 'ALTA' %}selected{% endif %}>🔴 ALTA</option>
                                                <option value="MEDIA" {% if m.prioridad == 'MEDIA' %}selected{% endif %}>🟡 MEDIA</option>
                                                <option value="BAJA" {% if m.prioridad == 'BAJA' %}selected{% endif %}>🟢 BAJA</option>
                                                <option value="MANTENIMIENTO" {% if m.prioridad == 'MANTENIMIENTO' %}selected{% endif %}>⚪ MANTO</option>
                                            </select>
                                        </td>
                                        <td>
                                            <input type="text" name="motorizado" value="{{ m.motorizado }}" class="form-control form-control-sm">
                                        </td>
                                        <td>
                                            <div class="d-flex gap-1">
                                                <input class="btn-check" type="checkbox" name="lunes" id="l_{{m.id}}" {% if m.lunes %}checked{% endif %}>
                                                <label class="btn btn-outline-secondary btn-sm p-1" for="l_{{m.id}}">L</label>

                                                <input class="btn-check" type="checkbox" name="martes" id="m_{{m.id}}" {% if m.martes %}checked{% endif %}>
                                                <label class="btn btn-outline-secondary btn-sm p-1" for="m_{{m.id}}">M</label>

                                                <input class="btn-check" type="checkbox" name="miercoles" id="x_{{m.id}}" {% if m.miercoles %}checked{% endif %}>
                                                <label class="btn btn-outline-secondary btn-sm p-1" for="x_{{m.id}}">X</label>

                                                <input class="btn-check" type="checkbox" name="jueves" id="j_{{m.id}}" {% if m.jueves %}checked{% endif %}>
                                                <label class="btn btn-outline-secondary btn-sm p-1" for="j_{{m.id}}">J</label>

                                                <input class="btn-check" type="checkbox" name="viernes" id="v_{{m.id}}" {% if m.viernes %}checked{% endif %}>
                                                <label class="btn btn-outline-secondary btn-sm p-1" for="v_{{m.id}}">V</label>

                                                <input class="btn-check" type="checkbox" name="sabado" id="s_{{m.id}}" {% if m.sabado %}checked{% endif %}>
                                                <label class="btn btn-outline-primary btn-sm p-1" for="s_{{m.id}}">S</label>
                                            </div>
                                        </td>
                                        <td>
                                            <div class="d-flex gap-1">
                                                <button type="submit" class="btn btn-success btn-sm">💾</button>
                                                <a href="/admin/eliminar/{{ m.id }}" class="btn btn-danger btn-sm" onclick="return confirm('¿Eliminar máquina?')">🗑️</a>
                                            </div>
                                        </td>
                                    </form>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
"""

# ---------------------------------------------------------
# RUTAS DE LA APLICACIÓN
# ---------------------------------------------------------

@app.route("/")
def tv_view():
    return render_template_string(TV_HTML)

@app.route("/admin")
def admin_view():
    conn = get_db_connection()
    maquinas = conn.execute("SELECT * FROM maquinas ORDER BY id DESC").fetchall()
    conn.close()
    return render_template_string(ADMIN_HTML, maquinas=maquinas)

@app.route("/api/maquinas")
def api_maquinas():
    conn = get_db_connection()
    maquinas = conn.execute("SELECT * FROM maquinas ORDER BY id ASC").fetchall()
    conn.close()
    return jsonify([dict(m) for m in maquinas])

@app.route("/admin/agregar", methods=["POST"])
def admin_agregar():
    nombre = request.form.get("nombre")
    prioridad = request.form.get("prioridad")
    motorizado = request.form.get("motorizado") or "Sin Asignar"
    lunes = 1 if request.form.get("lunes") else 0
    martes = 1 if request.form.get("martes") else 0
    miercoles = 1 if request.form.get("miercoles") else 0
    jueves = 1 if request.form.get("jueves") else 0
    viernes = 1 if request.form.get("viernes") else 0
    sabado = 1 if request.form.get("sabado") else 0

    conn = get_db_connection()
    conn.execute("""
        INSERT INTO maquinas (nombre, prioridad, motorizado, lunes, martes, miercoles, jueves, viernes, sabado)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (nombre, prioridad, motorizado, lunes, martes, miercoles, jueves, viernes, sabado))
    conn.commit()
    conn.close()
    return redirect(url_for("admin_view"))

@app.route("/admin/editar/<int:id>", methods=["POST"])
def admin_editar(id):
    nombre = request.form.get("nombre")
    prioridad = request.form.get("prioridad")
    motorizado = request.form.get("motorizado") or "Sin Asignar"
    lunes = 1 if request.form.get("lunes") else 0
    martes = 1 if request.form.get("martes") else 0
    miercoles = 1 if request.form.get("miercoles") else 0
    jueves = 1 if request.form.get("jueves") else 0
    viernes = 1 if request.form.get("viernes") else 0
    sabado = 1 if request.form.get("sabado") else 0

    conn = get_db_connection()
    conn.execute("""
        UPDATE maquinas SET nombre=?, prioridad=?, motorizado=?, lunes=?, martes=?, miercoles=?, jueves=?, viernes=?, sabado=?
        WHERE id=?
    """, (nombre, prioridad, motorizado, lunes, martes, miercoles, jueves, viernes, sabado, id))
    conn.commit()
    conn.close()
    return redirect(url_for("admin_view"))

@app.route("/admin/eliminar/<int:id>")
def admin_eliminar(id):
    conn = get_db_connection()
    conn.execute("DELETE FROM maquinas WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for("admin_view"))

if __name__ == "__main__":
    init_db()
    print("Servidor iniciado en http://0.0.0.0:5000")
    print("Vista TV: http://<IP-LOCAL>:5000/")
    print("Panel Jefes: http://<IP-LOCAL>:5000/admin")
    app.run(host="0.0.0.0", port=5000, debug=True)
