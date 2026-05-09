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
# BOTONES ESTADO PENDIENTE
# ==========================================

def botones_pendiente(viaje_id):

    keyboard = [

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
    ]

    return InlineKeyboardMarkup(
        keyboard
    )

# ==========================================
# BOTONES ESTADO INICIADO
# ==========================================

def botones_iniciado(viaje_id):

    keyboard = [

        [

            InlineKeyboardButton(
                "✅ Finalizar viaje",
                callback_data=f"finalizar_{viaje_id}"
            ),

            InlineKeyboardButton(
                "🚫 Cancelado",
                callback_data=f"cancelado_{viaje_id}"
            )
        ]
    ]

    return InlineKeyboardMarkup(
        keyboard
    )