# ==========================================
# IMPORTS
# ==========================================

import state
import requests

from config import (
    TOKEN,
    CHAT_ID
)

# ==========================================
# ACTUALIZAR PANEL AUXILIAR
# ==========================================

def actualizar_panel_auxiliar(

    texto,
    reply_markup=None

):

    # ======================================
    # EDITAR SI EXISTE
    # ======================================

    if state.message_id_auxiliar:

        response = requests.post(

            f"https://api.telegram.org/bot{TOKEN}/editMessageText",

            json={

                "chat_id": CHAT_ID,

                "message_id":
                    state.message_id_auxiliar,

                "text": texto,

                "reply_markup":
                    reply_markup.to_dict()
                    if reply_markup
                    else None

            }

        )

        resultado = response.json()

        # ==================================
        # SI FALLA → CREAR NUEVO
        # ==================================

        if not resultado.get("ok"):

            state.message_id_auxiliar = None

            actualizar_panel_auxiliar(
                texto,
                reply_markup
            )

    # ======================================
    # CREAR NUEVO
    # ======================================

    else:

        response = requests.post(

            f"https://api.telegram.org/bot{TOKEN}/sendMessage",

            json={

                "chat_id": CHAT_ID,

                "text": texto,

                "reply_markup":
                    reply_markup.to_dict()
                    if reply_markup
                    else None

            }

        )

        resultado = response.json()

        state.message_id_auxiliar = (

            resultado["result"]["message_id"]

        )