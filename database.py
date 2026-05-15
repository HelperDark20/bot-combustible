# ==========================================
# IMPORTS
# ==========================================
import sqlite3
import state
from datetime import datetime

import pytz

from score import calcular_score

# ==========================================
# TIMEZONE COLOMBIA
# ==========================================

zona_colombia = pytz.timezone(
    "America/Bogota"
)

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

    with state.STATE_LOCK:

        (
            distancia_total,
            tiempo_total,
            dinero_por_km,
            dinero_por_min,
            score_visual,
            estado_score
        ) = calcular_score(data)

        fecha = datetime.now(
            zona_colombia
        ).strftime(
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
# BORRAR DÍA ESPECÍFICO
# ==========================================

def borrar_dia(fecha):

    with state.STATE_LOCK:

        cursor.execute("""

        DELETE FROM viajes

        WHERE DATE(fecha) = ?

        """, (fecha,))

        conn.commit()

# ==========================================
# ACTUALIZAR ESTADO
# ==========================================

def actualizar_estado(viaje_id, estado):

    with state.STATE_LOCK:

        ahora = datetime.now(
            zona_colombia
        ).strftime(
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