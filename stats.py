# ==========================================
# IMPORTS
# ==========================================
from database import cursor

# ==========================================
# OBTENER STATS
# ==========================================
def obtener_estadisticas():

    # ======================================
    # TOTAL VIAJES
    # ======================================

    cursor.execute("""
    SELECT COUNT(*)
    FROM viajes
    """)

    total = cursor.fetchone()[0]

    # ======================================
    # GANANCIA TOTAL
    # ======================================

    cursor.execute("""
    SELECT SUM(dinero)
    FROM viajes
    WHERE estado='aceptado'
    """)

    dinero_total = cursor.fetchone()[0]

    if dinero_total is None:
        dinero_total = 0

    # ======================================
    # PROMEDIO SCORE
    # ======================================

    cursor.execute("""
    SELECT AVG(score_visual)
    FROM viajes
    WHERE estado='aceptado'
    """)

    promedio = cursor.fetchone()[0]

    if promedio is None:
        promedio = 0

    promedio = round(promedio, 1)

    # ======================================
    # ACEPTADOS
    # ======================================

    cursor.execute("""
    SELECT COUNT(*)
    FROM viajes
    WHERE estado='aceptado'
    """)

    aceptados = cursor.fetchone()[0]

    # ======================================
    # RECHAZADOS
    # ======================================

    cursor.execute("""
    SELECT COUNT(*)
    FROM viajes
    WHERE estado='rechazado'
    """)

    rechazados = cursor.fetchone()[0]

    # ======================================
    # CANCELADOS
    # ======================================

    cursor.execute("""
    SELECT COUNT(*)
    FROM viajes
    WHERE estado='cancelado'
    """)

    cancelados = cursor.fetchone()[0]

    # ======================================
    # RESPUESTA
    # ======================================

    respuesta = (

        "📊 ESTADÍSTICAS\n\n"

        f"🚘 Viajes:\n{total}\n\n"

        f"✅ Aceptados:\n{aceptados}\n\n"

        f"❌ Rechazados:\n{rechazados}\n\n"

        f"🚫 Cancelados:\n{cancelados}\n\n"

        f"💰 Ganancia:\n"
        f"{dinero_total:,} COP\n\n"

        f"⭐ Score promedio:\n"
        f"{promedio}/10"
    )

    return respuesta