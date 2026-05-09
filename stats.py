# ==========================================
# IMPORTS
# ==========================================
from database import cursor

from fuel import (

    calcular_gasto_combustible_total,

    calcular_combustible_restante

)

# ==========================================
# ESTADÍSTICAS HOY
# ==========================================

def obtener_estadisticas_hoy():

    cursor.execute("""

    SELECT COUNT(*)

    FROM viajes

    WHERE DATE(fecha) = DATE('now', '-5 hours')

    """)

    viajes = cursor.fetchone()[0]

    # ======================================
    # COMPLETADOS
    # ======================================

    cursor.execute("""

    SELECT COUNT(*)

    FROM viajes

    WHERE estado='completado'

    AND DATE(fecha) = DATE('now', '-5 hours')

    """)

    completados = cursor.fetchone()[0]

    # ======================================
    # CANCELADOS
    # ======================================

    cursor.execute("""

    SELECT COUNT(*)

    FROM viajes

    WHERE estado='cancelado'

    AND DATE(fecha) = DATE('now', '-5 hours')

    """)

    cancelados = cursor.fetchone()[0]

    # ======================================
    # GANANCIA TOTAL
    # ======================================

    cursor.execute("""

    SELECT SUM(dinero)

    FROM viajes

    WHERE estado='completado'

    AND DATE(fecha) = DATE('now', '-5 hours')

    """)

    ganancia_total = cursor.fetchone()[0]

    if ganancia_total is None:

        ganancia_total = 0

    return (

        "📆 HISTORIAL HOY\n\n"

        f"🚘 Viajes:\n"
        f"{viajes}\n\n"

        f"✅ Completados:\n"
        f"{completados}\n\n"

        f"🚫 Cancelados:\n"
        f"{cancelados}\n\n"

        f"💰 Ganancia:\n"
        f"{ganancia_total:,.0f} COP"

    )

# ==========================================
# ESTADÍSTICAS SEMANA
# ==========================================

def obtener_estadisticas_semana():

    cursor.execute("""

    SELECT COUNT(*)

    FROM viajes

    WHERE strftime('%W', fecha)
    =
    strftime('%W', 'now', '-5 hours')

    """)

    viajes = cursor.fetchone()[0]

    # ======================================
    # COMPLETADOS
    # ======================================

    cursor.execute("""

    SELECT COUNT(*)

    FROM viajes

    WHERE estado='completado'

    AND strftime('%W', fecha)
    =
    strftime('%W', 'now', '-5 hours')

    """)

    completados = cursor.fetchone()[0]

    # ======================================
    # CANCELADOS
    # ======================================

    cursor.execute("""

    SELECT COUNT(*)

    FROM viajes

    WHERE estado='cancelado'

    AND strftime('%W', fecha)
    =
    strftime('%W', 'now', '-5 hours')

    """)

    cancelados = cursor.fetchone()[0]

    # ======================================
    # GANANCIA TOTAL
    # ======================================

    cursor.execute("""

    SELECT SUM(dinero)

    FROM viajes

    WHERE estado='completado'

    AND strftime('%W', fecha)
    =
    strftime('%W', 'now', '-5 hours')

    """)

    ganancia_total = cursor.fetchone()[0]

    if ganancia_total is None:

        ganancia_total = 0

    return (

        "📅 HISTORIAL SEMANA\n\n"

        f"🚘 Viajes:\n"
        f"{viajes}\n\n"

        f"✅ Completados:\n"
        f"{completados}\n\n"

        f"🚫 Cancelados:\n"
        f"{cancelados}\n\n"

        f"💰 Ganancia:\n"
        f"{ganancia_total:,.0f} COP"

    )

# ==========================================
# ESTADÍSTICAS MES
# ==========================================

def obtener_estadisticas_mes():

    cursor.execute("""

    SELECT COUNT(*)

    FROM viajes

    WHERE strftime('%m', fecha)
    =
    strftime('%m', 'now', '-5 hours')

    """)

    viajes = cursor.fetchone()[0]

    # ======================================
    # COMPLETADOS
    # ======================================

    cursor.execute("""

    SELECT COUNT(*)

    FROM viajes

    WHERE estado='completado'

    AND strftime('%m', fecha)
    =
    strftime('%m', 'now', '-5 hours')

    """)

    completados = cursor.fetchone()[0]

    # ======================================
    # CANCELADOS
    # ======================================

    cursor.execute("""

    SELECT COUNT(*)

    FROM viajes

    WHERE estado='cancelado'

    AND strftime('%m', fecha)
    =
    strftime('%m', 'now', '-5 hours')

    """)

    cancelados = cursor.fetchone()[0]

    # ======================================
    # GANANCIA TOTAL
    # ======================================

    cursor.execute("""

    SELECT SUM(dinero)

    FROM viajes

    WHERE estado='completado'

    AND strftime('%m', fecha)
    =
    strftime('%m', 'now', '-5 hours')

    """)

    ganancia_total = cursor.fetchone()[0]

    if ganancia_total is None:

        ganancia_total = 0

    return (

        "🗓 HISTORIAL MES\n\n"

        f"🚘 Viajes:\n"
        f"{viajes}\n\n"

        f"✅ Completados:\n"
        f"{completados}\n\n"

        f"🚫 Cancelados:\n"
        f"{cancelados}\n\n"

        f"💰 Ganancia:\n"
        f"{ganancia_total:,.0f} COP"

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