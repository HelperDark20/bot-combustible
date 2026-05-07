# ==========================================
# IMPORTS
# ==========================================
from telegram import (

    InlineKeyboardButton,

    InlineKeyboardMarkup
)

# ==========================================
# MENU PRINCIPAL
# ==========================================
def menu_principal():

    keyboard = [

        [
            InlineKeyboardButton(
                "📸 Analizar viaje",
                callback_data="analizar"
            )
        ],

        [
            InlineKeyboardButton(
                "🚘 Ver viajes",
                callback_data="ver_viajes"
            )
        ],

        [
            InlineKeyboardButton(
                "📊 Estadísticas",
                callback_data="stats"
            )
        ],

        [
            InlineKeyboardButton(
                "⛽ Configuración",
                callback_data="config"
            )
        ],
        
        [
            InlineKeyboardButton(
                "🗑 Reiniciar día",
                callback_data="reiniciar"
            )
        ]
    ]

    return InlineKeyboardMarkup(
        keyboard
    )

# ==========================================
# BOTONES VIAJE
# ==========================================
def botones_viaje(viaje_id):

    keyboard = [

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
    ]

    return InlineKeyboardMarkup(
        keyboard
    )

# ==========================================
# BOTON CANCELAR
# ==========================================
def boton_cancelar(viaje_id):

    keyboard = [

        [

            InlineKeyboardButton(
                "🚫 Cancelar viaje",
                callback_data=f"cancelar_{viaje_id}"
            )
        ]
    ]

    return InlineKeyboardMarkup(
        keyboard
    )