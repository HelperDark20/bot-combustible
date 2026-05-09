# ==========================================
# IMPORTS
# ==========================================
from database import cursor

from fuel import (

    calcular_gasto_combustible_total,

    calcular_combustible_restante

)

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
    WHERE estado='completado'
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
    WHERE estado='completado'
    """)

    promedio = cursor.fetchone()[0]

    if promedio is None:
        promedio = 0

    promedio = round(promedio, 1)

    # ======================================
    # COMPLETADOS
    # ======================================

    cursor.execute("""
    SELECT COUNT(*)
    FROM viajes
    WHERE estado='completado'
    """)

    completados = cursor.fetchone()[0]

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
    # COMBUSTIBLE
    # ======================================

    gasto_combustible = (
        calcular_gasto_combustible_total()
    )

    combustible_restante = (
        calcular_combustible_restante()
    )

    ganancia_neta = (
        dinero_total - gasto_combustible
    )

    # ======================================
    # RESPUESTA
    # ======================================

    respuesta = (

        "📊 ESTADÍSTICAS\n\n"

        f"🚘 Viajes:\n{total}\n\n"

        f"✅ Completados:\n{completados}\n\n"

        f"🚫 Cancelados:\n{cancelados}\n\n"

        f"💰 Ganancia bruta:\n"
        f"{dinero_total:,.0f} COP\n\n"

        f"⛽ Gasto combustible:\n"
        f"{gasto_combustible:,.0f} COP\n\n"

        f"🛢 Combustible restante:\n"
        f"{combustible_restante:,.0f} COP\n\n"

        f"💵 Ganancia neta:\n"
        f"{ganancia_neta:,.0f} COP\n\n"

        f"⭐ Score promedio:\n"
        f"{promedio}/10"
    )

    return respuesta