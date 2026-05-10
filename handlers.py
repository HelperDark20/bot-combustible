# =========================================
# HANDLERS.PY
# =========================================

import state

from ui_operativa import (
    render_operativo
)

from telegram import (
    Update
)

from telegram.ext import (
    ContextTypes
)

from telegram_ui import (
    menu_principal,
    menu_historial,
    menu_configuracion
)

from state import (
    usuarios_configurando,
    usuarios_borrando_fecha
)

from database import (
    actualizar_estado,
    borrar_dia
)

from stats import (
    obtener_estadisticas,
    obtener_estadisticas_hoy,
    obtener_estadisticas_semana,
    obtener_estadisticas_mes
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

    # ======================================
    # VER VIAJE EN CURSO
    # ======================================

    if query.data == "ver_curso":

        state.vista_actual = "curso"

        texto, reply_markup = (
            render_operativo()
        )

        await query.edit_message_text(

            text=texto,

            reply_markup=reply_markup

        )

    # ======================================
    # VER VIAJE PENDIENTE
    # ======================================

    elif query.data == "ver_pendiente":

        state.vista_actual = "pendiente"

        texto, reply_markup = (
            render_operativo()
        )

        await query.edit_message_text(

            text=texto,

            reply_markup=reply_markup

        )

    # ======================================
    # INICIAR VIAJE
    # ======================================

    elif query.data == "iniciar_viaje":

        # ==================================
        # SI HAY PENDIENTE
        # ==================================

        if state.viaje_pendiente:

            state.viaje_en_curso = (
                state.viaje_pendiente.copy()
            )

            state.viaje_pendiente = None

        # ==================================
        # INICIAR ACTUAL
        # ==================================

        if state.viaje_en_curso:

            actualizar_estado(

                state.viaje_en_curso["id"],

                "iniciado"

            )

            state.viaje_en_curso[
                "estado_operativo"
            ] = "curso"

        state.vista_actual = "curso"

        # ==================================
        # RERENDER
        # ==================================

        texto, reply_markup = (
            render_operativo()
        )

        await query.edit_message_text(

            text=texto,

            reply_markup=reply_markup

        )

    # ======================================
    # FINALIZAR VIAJE
    # ======================================

    elif query.data == "finalizar_viaje":

        # ==================================
        # SI HAY PENDIENTE
        # ==================================

        if state.viaje_en_curso:

            actualizar_estado(

                state.viaje_en_curso["id"],

                "completado"

            )

        if state.viaje_pendiente:

            state.viaje_en_curso = (
                state.viaje_pendiente.copy()
            )

            state.viaje_pendiente = None

            state.viaje_en_curso[
                "estado_operativo"
            ] = "curso"

            state.vista_actual = "curso"

        # ==================================
        # SI NO HAY MÁS VIAJES
        # ==================================

        else:

            state.viaje_en_curso = None

            state.vista_actual = "curso"

        # ==================================
        # RERENDER
        # ==================================

        texto, reply_markup = (
            render_operativo()
        )

        await query.edit_message_text(

            text=texto,

            reply_markup=reply_markup

        )

    # ======================================
    # CANCELAR VIAJE
    # ======================================

    elif query.data == "cancelar_viaje":

        # ==================================
        # CANCELAR VIAJE EN CURSO
        # ==================================

        if state.vista_actual == "curso":


            if state.viaje_en_curso:

                actualizar_estado(

                    state.viaje_en_curso["id"],

                    "cancelado"

                )


            # si hay pendiente → pasa a curso

            if state.viaje_pendiente:

                state.viaje_en_curso = (
                    state.viaje_pendiente.copy()
                )

                state.viaje_pendiente = None

                state.viaje_en_curso[
                    "estado_operativo"
                ] = "curso"

            # si no hay más viajes

            else:

                state.viaje_en_curso = None

        # ==================================
        # CANCELAR PENDIENTE
        # ==================================

        elif state.vista_actual == "pendiente":

            if state.viaje_pendiente:

                actualizar_estado(

                    state.viaje_pendiente["id"],

                    "cancelado"

                )

            state.viaje_pendiente = None

            state.vista_actual = "curso"

        # ==================================
        # RERENDER
        # ==================================

        texto, reply_markup = (
            render_operativo()
        )

        await query.edit_message_text(

            text=texto,

            reply_markup=reply_markup

        )

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

        keyboard = menu_configuracion()

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
    # HISTORIAL SEMANA
    # =====================================

    elif query.data == "historial_semana":

        texto = obtener_estadisticas_semana()

        await query.message.reply_text(
            texto
        )

    # =====================================
    # HISTORIAL MES
    # =====================================

    elif query.data == "historial_mes":

        texto = obtener_estadisticas_mes()

        await query.message.reply_text(
            texto
        )

    # =====================================
    # HISTORIAL TOTAL
    # =====================================

    elif query.data == "historial_total":

        texto = obtener_estadisticas()

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
    # VOLVER MENÚ
    # =====================================

    elif query.data == "volver_menu":

        await query.message.reply_text(

            "🚖 BOT IA VIAJES\n\n"
            "Selecciona una opción:",

            reply_markup=menu_principal()

        )

    # # =====================================
    # # INICIAR VIAJE
    # # =====================================

    # elif query.data.startswith("iniciar_"):

    #     viaje_id = int(
    #         query.data.split("_")[1]
    #     )

    #     actualizar_estado(
    #         viaje_id,
    #         "iniciado"
    #     )

    #     await query.message.reply_text(

    #         "🚖 Viaje iniciado.",

    #         reply_markup=botones_iniciado(
    #             viaje_id
    #         )
    #     )

    # # =====================================
    # # FINALIZAR VIAJE
    # # =====================================

    # elif query.data.startswith("finalizar_"):

    #     viaje_id = int(
    #         query.data.split("_")[1]
    #     )

    #     actualizar_estado(
    #         viaje_id,
    #         "completado"
    #     )

    #     await query.message.reply_text(
    #         "✅ Viaje finalizado."
    #     )

    # # =====================================
    # # CANCELADO
    # # =====================================

    # elif query.data.startswith("cancelado_"):

    #     viaje_id = int(
    #         query.data.split("_")[1]
    #     )

    #     actualizar_estado(
    #         viaje_id,
    #         "cancelado"
    #     )

    #     await query.message.reply_text(
    #         "🚫 Viaje cancelado."
    #     )

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

# # =========================================
# # RECIBIR IMAGEN
# # =========================================

# async def recibir_imagen(
#     update: Update,
#     context: ContextTypes.DEFAULT_TYPE
# ):

#     foto = update.message.photo[-1]

#     archivo = await foto.get_file()

#     ruta = "temp.jpg"

#     await archivo.download_to_drive(ruta)

#     resultado = analizar_imagen_openai(
#         ruta
#     )

#     if not resultado:

#         await update.message.reply_text(
#             "❌ No pude analizar la imagen."
#         )

#         return

#     try:

#         datos = json.loads(resultado)

#     except:

#         await update.message.reply_text(
#             "❌ Error leyendo datos IA."
#         )

#         return

#     tipo = datos.get(
#         "tipo_viaje",
#         "Desconocido"
#     )

#     ganancia = float(
#         datos.get("dinero", 0)
#     )

#     distancia = float(
#         datos.get(
#             "distancia_destino_km",
#             0
#         )
#     )

#     tiempo = int(
#         datos.get(
#             "tiempo_destino_min",
#             0
#         )
#     )

#     (
#         distancia_total,
#         tiempo_total,
#         dinero_por_km,
#         dinero_por_min,
#         score_visual,
#         estado_score
#     ) = calcular_score(datos)

#     viaje_id = guardar_viaje(datos)

#     keyboard = botones_pendiente(
#         viaje_id
#     )

#     texto = f"""
# 📲 VIA SHORTCUTS

# 🚘 {tipo}

# 💰 {ganancia:,.0f} COP
# 📍 {distancia} km
# ⏱ {tiempo} min

# 💸 {dinero_por_km:,.0f} COP/km
# ⌛ {dinero_por_min:,.0f} COP/min

# ⭐ Score: {score_visual}/10

# 🔥 {estado_score}
# """

#     await update.message.reply_text(
#         texto,
#         reply_markup=keyboard
#     )
