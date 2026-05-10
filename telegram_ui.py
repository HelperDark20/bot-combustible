# ==========================================
# IMPORTS
# ==========================================
from telegram import (

    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup
)

# ==========================================
# MENU PRINCIPAL
# ==========================================
def menu_principal():

    keyboard = [

        [
            InlineKeyboardButton(
                "📅 Historial",
                callback_data="historial"
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
# MENÚ HISTORIAL
# ==========================================

def menu_historial():

    keyboard = [

        [

            InlineKeyboardButton(
                "📆 Hoy",
                callback_data="historial_hoy"
            )

        ],

        [

            InlineKeyboardButton(
                "📅 Semana",
                callback_data="historial_semana"
            )

        ],

        [

            InlineKeyboardButton(
                "🗓 Mes",
                callback_data="historial_mes"
            )

        ],

        [

            InlineKeyboardButton(
                "📈 Total",
                callback_data="historial_total"
            )

        ],

        [

            InlineKeyboardButton(
                "⬅️ Volver",
                callback_data="volver_menu"
            )

        ]

    ]

    return InlineKeyboardMarkup(
        keyboard
    )

# ==========================================
# MENÚ CONFIGURACIÓN
# ==========================================

def menu_configuracion():

    keyboard = [

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

        ],

        [

            InlineKeyboardButton(
                "⬅️ Volver",
                callback_data="volver_menu"
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

# =========================================
# BOTÓN PERSISTENTE
# =========================================

def teclado_persistente():

    keyboard = [

        ["🚀 Iniciar Consulta"]

    ]

    return ReplyKeyboardMarkup(

        keyboard,

        resize_keyboard=True,

        is_persistent=True

    )