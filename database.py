# ==========================================
# IMPORTS
# ==========================================
import sqlite3

from datetime import datetime

from score import calcular_score

# ==========================================
# SQLITE
# ==========================================
conn = sqlite3.connect(

    "viajes.db",

    check_same_thread=False
)

cursor = conn.cursor()

# ==========================================
# TABLA VIAJES
# ==========================================
cursor.execute("""

CREATE TABLE IF NOT EXISTS viajes (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    fecha TEXT,

    tipo_viaje TEXT,

    dinero INTEGER,

    distancia_recogida REAL,

    distancia_destino REAL,

    tiempo_recogida INTEGER,

    tiempo_destino INTEGER,

    distancia_total REAL,

    tiempo_total INTEGER,

    score REAL,

    score_visual INTEGER,

    estado TEXT,

    hora_inicio TEXT,

    hora_fin TEXT
)

""")

conn.commit()

# ==========================================
# GUARDAR VIAJE
# ==========================================
def guardar_viaje(data):

    (
        distancia_total,
        tiempo_total,
        dinero_por_km,
        dinero_por_min,
        score_visual,
        estado_score
    ) = calcular_score(data)

    fecha = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    cursor.execute("""

    INSERT INTO viajes (

        fecha,
        tipo_viaje,
        dinero,
        distancia_recogida,
        distancia_destino,
        tiempo_recogida,
        tiempo_destino,
        distancia_total,
        tiempo_total,
        score,
        score_visual,
        estado

    )

    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)

    """, (

        fecha,

        data["tipo_viaje"],

        data["dinero"],

        data["distancia_recogida_km"],

        data["distancia_destino_km"],

        data["tiempo_recogida_min"],

        data["tiempo_destino_min"],

        distancia_total,

        tiempo_total,

        dinero_por_km,

        score_visual,

        "pendiente"
    ))

    conn.commit()

    return cursor.lastrowid

# ==========================================
# OBTENER VIAJES
# ==========================================

def obtener_viajes():

    cursor.execute("""

    SELECT *

    FROM viajes

    ORDER BY id DESC

    """)

    resultados = cursor.fetchall()

    viajes = []

    for viaje in resultados:

        viajes.append({

            "id": viaje[0],

            "fecha": viaje[1],

            "tipo_viaje": viaje[2],

            "dinero": viaje[3],

            "distancia_recogida": viaje[4],

            "distancia_destino": viaje[5],

            "tiempo_recogida": viaje[6],

            "tiempo_destino": viaje[7],

            "distancia_total": viaje[8],

            "tiempo_total": viaje[9],

            "score": viaje[10],

            "score_visual": viaje[11],

            "estado": viaje[12]

        })

    return viajes

# ==========================================
# REINICIAR DÍA
# ==========================================

def reiniciar_dia():

    cursor.execute("""

    DELETE FROM viajes

    """)

    conn.commit()

# ==========================================
# BORRAR DÍA ESPECÍFICO
# ==========================================

def borrar_dia(fecha):

    cursor.execute("""

    DELETE FROM viajes

    WHERE DATE(fecha) = ?

    """, (fecha,))

    conn.commit()

# ==========================================
# ACTUALIZAR ESTADO
# ==========================================

def actualizar_estado(viaje_id, estado):

    from datetime import datetime

    ahora = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    # ======================================
    # INICIADO
    # ======================================

    if estado == "iniciado":

        cursor.execute("""

        UPDATE viajes

        SET
            estado = ?,
            hora_inicio = ?

        WHERE id = ?

        """, (

            estado,
            ahora,
            viaje_id

        ))

    # ======================================
    # COMPLETADO
    # ======================================

    elif estado == "completado":

        cursor.execute("""

        UPDATE viajes

        SET
            estado = ?,
            hora_fin = ?

        WHERE id = ?

        """, (

            estado,
            ahora,
            viaje_id

        ))

    # ======================================
    # CANCELADO
    # ======================================

    else:

        cursor.execute("""

        UPDATE viajes

        SET estado = ?

        WHERE id = ?

        """, (

            estado,
            viaje_id

        ))

    conn.commit()