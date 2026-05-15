# =========================================
# FUEL.PY
# CONFIGURACIÓN Y CÁLCULOS COMBUSTIBLE
# =========================================

import state
import sqlite3

from config import (
    DEFAULT_KM_L,
    DEFAULT_VALOR_GALON,
    DEFAULT_TANQUE
)

from database import cursor

# =========================================
# CREAR TABLA CONFIG
# =========================================

def crear_tabla_config():

    conn = sqlite3.connect("viajes.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS configuracion (

            clave TEXT PRIMARY KEY,
            valor REAL

        )
    """)

    conn.commit()
    conn.close()

# =========================================
# GUARDAR CONFIG
# =========================================

def guardar_config(clave, valor):

    with state.STATE_LOCK:

        conn = sqlite3.connect("viajes.db")
        cursor = conn.cursor()

        cursor.execute("""

            INSERT OR REPLACE INTO configuracion
            (clave, valor)

            VALUES (?, ?)

        """, (clave, valor))

        conn.commit()
        conn.close()

# =========================================
# OBTENER CONFIG
# =========================================

def obtener_config(clave):

    with state.STATE_LOCK:

        conn = sqlite3.connect("viajes.db")
        cursor = conn.cursor()

        cursor.execute("""

            SELECT valor
            FROM configuracion

            WHERE clave = ?

        """, (clave,))

        resultado = cursor.fetchone()

        conn.close()

        if resultado:
            return resultado[0]

        # =========================
        # DEFAULTS
        # =========================

        defaults = {

            "km_l": DEFAULT_KM_L,
            "valor_galon": DEFAULT_VALOR_GALON,
            "tanque": DEFAULT_TANQUE

        }

        return defaults.get(clave, 0)

# =========================================
# COSTO POR KM
# =========================================

def calcular_costo_km():

    km_l = obtener_config("km_l")

    valor_galon = obtener_config(
        "valor_galon"
    )

    # 1 galón = 3.785 litros

    km_por_galon = km_l * 3.785

    if km_por_galon <= 0:
        return 0

    costo_km = valor_galon / km_por_galon

    return round(costo_km, 2)

# =========================================
# GANANCIA NETA
# =========================================

def calcular_ganancia_neta(
    ganancia,
    distancia_km
):

    costo_km = calcular_costo_km()

    gasto_combustible = (
        distancia_km * costo_km
    )

    neta = ganancia - gasto_combustible

    return round(neta, 2)

# =========================================
# GASTO COMBUSTIBLE TOTAL
# =========================================

def calcular_gasto_combustible_total():

    with state.STATE_LOCK:

        costo_km = calcular_costo_km()

        cursor.execute("""

        SELECT SUM(distancia_total)

        FROM viajes

        WHERE estado='completado'

        """)

        resultado = cursor.fetchone()[0]

        if resultado is None:

            resultado = 0

        gasto_total = (
            resultado * costo_km
        )

        return round(gasto_total, 2)

# =========================================
# COMBUSTIBLE RESTANTE
# =========================================

def calcular_combustible_restante():

    tanque = obtener_config(
        "tanque"
    )

    gasto = (
        calcular_gasto_combustible_total()
    )

    restante = tanque - gasto

    if restante < 0:
        restante = 0

    return round(restante, 2)

# =========================================
# RESUMEN CONFIG
# =========================================

def obtener_resumen_combustible():

    km_l = obtener_config("km_l")

    valor_galon = obtener_config(
        "valor_galon"
    )

    tanque = obtener_config("tanque")

    costo_km = calcular_costo_km()

    gasto_total = (
        calcular_gasto_combustible_total()
    )

    restante = (
        calcular_combustible_restante()
    )

    return f"""

⛽ CONFIGURACIÓN ACTUAL

🚘 KM/L:
{km_l}

💰 Valor galón:
{valor_galon:,.0f} COP

🛢 Tanque:
{tanque:,.0f} COP

📉 Costo por KM:
{costo_km:,.0f} COP/km

⛽ Gasto combustible:
{gasto_total:,.0f} COP

🛢 Restante tanque:
{restante:,.0f} COP

"""