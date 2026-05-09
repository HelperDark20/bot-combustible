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
    menu_principal,
    botones_iniciado,
    menu_historial
)

from state import (
    usuarios_esperando_foto,
    usuarios_configurando,
    usuarios_borrando_fecha
)

from database import (
    guardar_viaje,
    obtener_viajes,
    reiniciar_dia,
    actualizar_estado,
    borrar_dia
)

from ocr import (
    analizar_imagen_openai
)

from score import (
    calcular_score
)

from stats import (
    obtener_estadisticas,
    obtener_estadisticas_hoy
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
    # ESTADÍSTICAS
    # =====================================

    if query.data == "stats":

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
    # HISTORIAL HOY
    # =====================================

    elif query.data == "historial_hoy":

        texto = obtener_estadisticas_hoy()

        await query.message.reply_text(
            texto
        )

    # =====================================
    # REINICIAR DÍA
    # =====================================

    elif query.data == "reiniciar":

        usuarios_borrando_fecha.add(
            query.from_user.id
        )

        await query.message.reply_text(

            "📅 Ingresa la fecha a borrar:\n\n"
            "DD/MM/AAAA"

        )

    # =====================================
    # HISTORIAL
    # =====================================

    elif query.data == "historial":

        await query.message.reply_text(

            "📅 HISTORIAL\n\n"
            "Selecciona una opción:",

            reply_markup=menu_historial()

        )

    # =====================================
    # INICIAR VIAJE
    # =====================================

    elif query.data.startswith("iniciar_"):

        viaje_id = int(
            query.data.split("_")[1]
        )

        actualizar_estado(
            viaje_id,
            "iniciado"
        )

        await query.message.reply_text(

            "🚖 Viaje iniciado.",

            reply_markup=botones_iniciado(
                viaje_id
            )
        )

    # =====================================
    # FINALIZAR VIAJE
    # =====================================

    elif query.data.startswith("finalizar_"):

        viaje_id = int(
            query.data.split("_")[1]
        )

        actualizar_estado(
            viaje_id,
            "completado"
        )

        await query.message.reply_text(
            "✅ Viaje finalizado."
        )

    # =====================================
    # CANCELADO
    # =====================================

    elif query.data.startswith("cancelado_"):

        viaje_id = int(
            query.data.split("_")[1]
        )

        actualizar_estado(
            viaje_id,
            "cancelado"
        )

        await query.message.reply_text(
            "🚫 Viaje cancelado."
        )

# =========================================
# RECIBIR TEXTO CONFIG
# =========================================

async def recibir_texto(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    user_id = update.message.from_user.id

    # =====================================
    # BORRAR FECHA
    # =====================================

    if user_id in usuarios_borrando_fecha:

        try:

            fecha = update.message.text

            dia, mes, anio = fecha.split("/")

            fecha_sql = (
                f"{anio}-{mes}-{dia}"
            )

            borrar_dia(fecha_sql)

            usuarios_borrando_fecha.remove(
                user_id
            )

            await update.message.reply_text(

                f"🗑 Día borrado:\n{fecha}"

            )

        except:

            await update.message.reply_text(

                "❌ Usa formato:\nDD/MM/AAAA"

            )

        return

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
                "🚖 Iniciar viaje",
                callback_data=f"iniciar_{viaje_id}"
            ),

            InlineKeyboardButton(
                "🚫 Cancelado",
                callback_data=f"cancelado_{viaje_id}"
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

# =========================================
# BORRAR FECHA
# =========================================

async def borrar_fecha(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    try:

        fecha = context.args[0]

        dia, mes, anio = fecha.split("/")

        fecha_sql = (
            f"{anio}-{mes}-{dia}"
        )

        borrar_dia(fecha_sql)

        await update.message.reply_text(

            f"🗑 Estadísticas borradas:\n{fecha}"

        )

    except:

        await update.message.reply_text(

            "❌ Usa:\n/borrar 09/05/2026"

        )