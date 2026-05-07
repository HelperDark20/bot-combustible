# ==========================================
# IMPORTS
# ==========================================
from telegram import Update

from telegram.ext import ContextTypes

from ocr import analizar_imagen_gpt

from score import construir_respuesta

from database import (

    guardar_viaje,
    cursor,
    conn
)

from stats import obtener_stats

from telegram_ui import (

    menu_principal,
    botones_viaje,
    boton_cancelar
)

import json

# ==========================================
# VARIABLES
# ==========================================
from state import usuarios_esperando_foto

# ==========================================
# START
# ==========================================
async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    await update.message.reply_text(

        "🚖 BOT IA VIAJES\n\n"
        "Selecciona una opción:",

        reply_markup=menu_principal()
    )

# ==========================================
# VER VIAJES
# ==========================================
async def mostrar_viajes(query):

    cursor.execute("""

    SELECT
    id,
    tipo_viaje,
    dinero,
    score_visual,
    estado

    FROM viajes

    ORDER BY id DESC

    LIMIT 15

    """)

    viajes = cursor.fetchall()

    if not viajes:

        await query.message.reply_text(
            "❌ No hay viajes."
        )

        return

    for viaje in viajes:

        viaje_id = viaje[0]

        texto = (

            f"🚘 {viaje[1]}\n\n"

            f"💰 {viaje[2]:,} COP\n"

            f"⭐ {viaje[3]}/10\n"

            f"📌 Estado: {viaje[4]}"
        )

        await query.message.reply_text(

            texto,

            reply_markup=boton_cancelar(
                viaje_id
            )
        )

# ==========================================
# BOTONES
# ==========================================
async def botones(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    await query.answer()

    user_id = query.from_user.id

    data = query.data

    # ======================================
    # ANALIZAR
    # ======================================

    if data == "analizar":

        usuarios_esperando_foto.add(
            user_id
        )

        await query.message.reply_text(
            "📸 Envíame la captura."
        )

    # ======================================
    # VER VIAJES
    # ======================================

    elif data == "ver_viajes":

        await mostrar_viajes(query)

    # ======================================
    # STATS
    # ======================================

    elif data == "stats":

        await query.message.reply_text(
            obtener_stats()
        )

    # ======================================
    # REINICIAR
    # ======================================

    elif data == "reiniciar":

        cursor.execute("""
        DELETE FROM viajes
        """)

        conn.commit()

        await query.message.reply_text(
            "🗑 Día reiniciado."
        )

    # ======================================
    # ACEPTADO
    # ======================================

    elif data.startswith("aceptado_"):

        viaje_id = data.split("_")[1]

        cursor.execute("""

        UPDATE viajes

        SET estado='aceptado'

        WHERE id=?

        """, (viaje_id,))

        conn.commit()

        await query.message.reply_text(
            "✅ Viaje aceptado."
        )

    # ======================================
    # RECHAZADO
    # ======================================

    elif data.startswith("rechazado_"):

        viaje_id = data.split("_")[1]

        cursor.execute("""

        UPDATE viajes

        SET estado='rechazado'

        WHERE id=?

        """, (viaje_id,))

        conn.commit()

        await query.message.reply_text(
            "❌ Viaje rechazado."
        )

    # ======================================
    # CANCELADO
    # ======================================

    elif data.startswith("cancelar_"):

        viaje_id = data.split("_")[1]

        cursor.execute("""

        UPDATE viajes

        SET estado='cancelado'

        WHERE id=?

        """, (viaje_id,))

        conn.commit()

        await query.message.reply_text(
            "🚫 Viaje cancelado."
        )

# ==========================================
# RECIBIR IMAGEN
# ==========================================
async def recibir_imagen(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    user_id = update.effective_user.id

    if user_id not in usuarios_esperando_foto:
        return

    try:

        foto = update.message.photo[-1]

        archivo = await foto.get_file()

        ruta = f"captura_{user_id}.jpg"

        await archivo.download_to_drive(
            ruta
        )

        await update.message.reply_text(
            "🧠 Analizando..."
        )

        respuesta_gpt = analizar_imagen_gpt(
            ruta
        )

        respuesta_gpt = (

            respuesta_gpt

            .replace("```json", "")

            .replace("```", "")

            .strip()
        )

        data = json.loads(
            respuesta_gpt
        )

        viaje_id = guardar_viaje(data)

        respuesta = construir_respuesta(
            data
        )

        await update.message.reply_text(

            respuesta,

            reply_markup=botones_viaje(
                viaje_id
            )
        )

        usuarios_esperando_foto.remove(
            user_id
        )

    except Exception as e:

        print(e)

        await update.message.reply_text(
            f"❌ Error:\n{e}"
        )