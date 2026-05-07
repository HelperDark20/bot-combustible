# =========================================
# HANDLERS.PY
# =========================================

import json

from telegram import (
    Update,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

from telegram.ext import (
    ContextTypes
)

from telegram_ui import (
    menu_principal
)

from state import (
    usuarios_esperando_foto,
    usuarios_configurando
)

from database import (
    guardar_viaje,
    obtener_viajes,
    reiniciar_dia
)

from ocr import (
    analizar_imagen_openai
)

from score import (
    calcular_score
)

from stats import (
    obtener_estadisticas
)

from fuel import (

    obtener_resumen_combustible,

    guardar_config
)

# =========================================
# START
# =========================================

async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    await update.message.reply_text(
        "🚖 BOT IA VIAJES\n\n"
        "Selecciona una opción:",
        reply_markup=menu_principal()
    )

# =========================================
# CALLBACK BOTONES
# =========================================

async def botones_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    await query.answer()

    # =====================================
    # ANALIZAR
    # =====================================

    if query.data == "analizar":

        usuarios_esperando_foto.add(
            query.from_user.id
        )

        await query.message.reply_text(
            "📸 Envíame la captura."
        )

    # =====================================
    # VER VIAJES
    # =====================================

    elif query.data == "ver_viajes":

        viajes = obtener_viajes()

        if not viajes:

            await query.message.reply_text(
                "❌ No hay viajes guardados."
            )

            return

        texto = "🚗 VIAJES DEL DÍA\n\n"

        for viaje in viajes:

            texto += (
                f"💰 {viaje['dinero']:,.0f} COP\n"
                f"📍 {viaje['distancia_total']} km\n"
                f"⭐ {viaje['score_visual']}/10\n\n"
            )

        await query.message.reply_text(
            texto
        )

    # =====================================
    # ESTADÍSTICAS
    # =====================================

    elif query.data == "stats":

        texto = obtener_estadisticas()

        await query.message.reply_text(
            texto
        )

    # =====================================
    # CONFIGURACIÓN
    # =====================================

    elif query.data == "config":

        keyboard = InlineKeyboardMarkup([

            [

                InlineKeyboardButton(
                    "⛽ KM/L",
                    callback_data="set_kml"
                )

            ],

            [

                InlineKeyboardButton(
                    "💰 Valor galón",
                    callback_data="set_galon"
                )

            ],

            [

                InlineKeyboardButton(
                    "🛢 Tanque",
                    callback_data="set_tanque"
                )

            ]

        ])

        texto = obtener_resumen_combustible()

        await query.message.reply_text(

            texto,

            reply_markup=keyboard

        )

    # =====================================
    # CAMBIAR KM/L
    # =====================================

    elif query.data == "set_kml":

        usuarios_configurando[
            query.from_user.id
        ] = "km_l"

        await query.message.reply_text(
            "⛽ Envía nuevo KM/L"
        )

    # =====================================
    # CAMBIAR GALÓN
    # =====================================

    elif query.data == "set_galon":

        usuarios_configurando[
            query.from_user.id
        ] = "valor_galon"

        await query.message.reply_text(
            "💰 Envía nuevo valor galón"
        )

    # =====================================
    # CAMBIAR TANQUE
    # =====================================

    elif query.data == "set_tanque":

        usuarios_configurando[
            query.from_user.id
        ] = "tanque"

        await query.message.reply_text(
            "🛢 Envía nuevo valor tanque"
        )

    # =====================================
    # REINICIAR
    # =====================================

    elif query.data == "reiniciar":

        reiniciar_dia()

        await query.message.reply_text(
            "🗑 Día reiniciado."
        )

    # =====================================
    # ACEPTADO
    # =====================================

    elif query.data.startswith("aceptado_"):

        await query.message.reply_text(
            "✅ Viaje aceptado."
        )

    # =====================================
    # RECHAZADO
    # =====================================

    elif query.data.startswith("rechazado_"):

        await query.message.reply_text(
            "❌ Viaje rechazado."
        )

# =========================================
# RECIBIR TEXTO CONFIG
# =========================================

async def recibir_texto(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    user_id = update.message.from_user.id

    if user_id not in usuarios_configurando:
        return

    clave = usuarios_configurando[user_id]

    try:

        valor = float(
            update.message.text
        )

    except:

        await update.message.reply_text(
            "❌ Envía solo números."
        )

        return

    guardar_config(
        clave,
        valor
    )

    del usuarios_configurando[user_id]

    texto = obtener_resumen_combustible()

    await update.message.reply_text(

        "✅ Configuración actualizada.\n"
        + texto

    )

# =========================================
# RECIBIR IMAGEN
# =========================================

async def recibir_imagen(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    user_id = update.message.from_user.id

    if user_id not in usuarios_esperando_foto:
        return

    usuarios_esperando_foto.remove(user_id)

    foto = update.message.photo[-1]

    archivo = await foto.get_file()

    ruta = "temp.jpg"

    await archivo.download_to_drive(ruta)

    resultado = analizar_imagen_openai(
        ruta
    )

    if not resultado:

        await update.message.reply_text(
            "❌ No pude analizar la imagen."
        )

        return

    try:

        datos = json.loads(resultado)

    except:

        await update.message.reply_text(
            "❌ Error leyendo datos IA."
        )

        return

    tipo = datos.get(
        "tipo_viaje",
        "Desconocido"
    )

    ganancia = float(
        datos.get("dinero", 0)
    )

    distancia = float(
        datos.get(
            "distancia_destino_km",
            0
        )
    )

    tiempo = int(
        datos.get(
            "tiempo_destino_min",
            0
        )
    )

    score, mensaje = calcular_score(
        ganancia,
        distancia
    )

    cop_km = (
        ganancia / distancia
        if distancia > 0 else 0
    )

    cop_min = (
        ganancia / tiempo
        if tiempo > 0 else 0
    )

    viaje_id = guardar_viaje(datos)

    keyboard = InlineKeyboardMarkup([

        [

            InlineKeyboardButton(
                "✅ Aceptado",
                callback_data=f"aceptado_{viaje_id}"
            ),

            InlineKeyboardButton(
                "❌ Rechazado",
                callback_data=f"rechazado_{viaje_id}"
            )

        ]

    ])

    texto = f"""
📲 VIA SHORTCUTS

🚘 {tipo}

💰 {ganancia:,.0f} COP
📍 {distancia} km
⏱ {tiempo} min

💸 {cop_km:,.0f} COP/km
⌛ {cop_min:,.0f} COP/min

⭐ Score: {score}/10

🔥 {mensaje}
"""

    await update.message.reply_text(
        texto,
        reply_markup=keyboard
    )