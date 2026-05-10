# ==========================================
# IMPORTS
# ==========================================

from telegram import (

    InlineKeyboardButton,
    InlineKeyboardMarkup

)

import state

# ==========================================
# RENDER PANEL OPERATIVO
# ==========================================

def render_operativo():

    texto = ""

    keyboard = []

    # ======================================
    # BOTONES SUPERIORES
    # ======================================

    if state.viaje_en_curso and state.viaje_pendiente:

        keyboard.append([

            InlineKeyboardButton(
                "🚘 Viaje En Curso",
                callback_data="ver_curso"
            ),

            InlineKeyboardButton(
                "⏳ Viaje Pendiente",
                callback_data="ver_pendiente"
            )

        ])

    # ======================================
    # MOSTRAR VIAJE ACTUAL
    # ======================================

    viaje = None

    if state.vista_actual == "curso":

        viaje = state.viaje_en_curso

    elif state.vista_actual == "pendiente":

        viaje = state.viaje_pendiente

    # ======================================
    # SI NO HAY VIAJES
    # ======================================

    if not viaje:

        texto = (
            "🚖 Sin viajes activos"
        )

        return texto, InlineKeyboardMarkup(
            keyboard
        )

    # ======================================
    # TEXO VIAJE
    # ======================================

    texto = (

        f"💰 {viaje['ganancia']:,.0f} COP\n"
        f"📍 {viaje['distancia_total']} km\n"
        f"⏱ {viaje['tiempo_total']} min\n\n"

        f"💵 {viaje['dinero_por_km']:,.0f} COP/KM\n"
        f"💸 {viaje['dinero_por_min']:,.0f} COP/MIN\n\n"

        f"⭐ {viaje['score_visual']}/10\n"
        f"🔥 {viaje['estado_score']}"

    )

    # ======================================
    # BOTONES SEGÚN VISTA
    # ======================================

    if state.vista_actual == "curso":

        keyboard.append([

            InlineKeyboardButton(
                "✅ Finalizar",
                callback_data="finalizar_viaje"
            ),

            InlineKeyboardButton(
                "🚫 Cancelar",
                callback_data="cancelar_viaje"
            )

        ])

    elif state.vista_actual == "pendiente":

        keyboard.append([

            InlineKeyboardButton(
                "🚘 Iniciar Viaje",
                callback_data="iniciar_viaje"
            ),

            InlineKeyboardButton(
                "🚫 Cancelar",
                callback_data="cancelar_viaje"
            )

        ])
    
    return texto, InlineKeyboardMarkup(
        keyboard
    )