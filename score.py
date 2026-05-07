# ==========================================
# SCORE REALISTA
# ==========================================
def calcular_score(data):

    dinero = data["dinero"]

    distancia_total = (

        data["distancia_recogida_km"]

        +

        data["distancia_destino_km"]
    )

    tiempo_total = (

        data["tiempo_recogida_min"]

        +

        data["tiempo_destino_min"]
    )

    # ======================================
    # DINERO POR KM
    # ======================================

    dinero_por_km = 0

    try:

        if distancia_total > 0:

            dinero_por_km = round(

                dinero / distancia_total,

                2
            )

    except:
        pass

    # ======================================
    # DINERO POR MIN
    # ======================================

    dinero_por_min = 0

    try:

        if tiempo_total > 0:

            dinero_por_min = round(

                dinero / tiempo_total,

                2
            )

    except:
        pass

    # ======================================
    # SCORE VISUAL
    # ======================================

    if dinero_por_km < 700:

        score_visual = 1

    elif dinero_por_km < 900:

        score_visual = 3

    elif dinero_por_km < 1000:

        score_visual = 5

    elif dinero_por_km < 1200:

        score_visual = 6

    elif dinero_por_km < 1400:

        score_visual = 7

    elif dinero_por_km < 1700:

        score_visual = 8

    elif dinero_por_km < 2000:

        score_visual = 9

    else:

        score_visual = 10

    # ======================================
    # ESTADO SCORE
    # ======================================

    if score_visual <= 3:

        estado_score = "❌ Poco rentable"

    elif score_visual <= 6:

        estado_score = "⚠️ Regular"

    elif score_visual <= 8:

        estado_score = "✅ Buen viaje"

    else:

        estado_score = "🔥 Excelente viaje"

    return (

        distancia_total,

        tiempo_total,

        dinero_por_km,

        dinero_por_min,

        score_visual,

        estado_score
    )

# ==========================================
# RESPUESTA
# ==========================================
def construir_respuesta(data):

    (
        distancia_total,
        tiempo_total,
        dinero_por_km,
        dinero_por_min,
        score_visual,
        estado_score
    ) = calcular_score(data)

    respuesta = (

        f"🚘 {data['tipo_viaje']}\n\n"

        f"💰 {data['dinero']:,} COP\n"

        f"📍 {distancia_total} km\n"

        f"⏱ {tiempo_total} min\n\n"

        f"💸 {dinero_por_km:,.0f} COP/km\n"

        f"⏳ {dinero_por_min:,.0f} COP/min\n\n"

        f"⭐ Score: {score_visual}/10\n\n"

        f"{estado_score}"
    )

    return respuesta