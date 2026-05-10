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

        json_data = {

            "chat_id": CHAT_ID,

            "message_id":
                state.message_id_auxiliar,

            "text": texto

        }

        if reply_markup:

            json_data[
                "reply_markup"
            ] = reply_markup.to_dict()

        response = requests.post(

            f"https://api.telegram.org/bot{TOKEN}/editMessageText",

            json=json_data

        )

        resultado = response.json()

        print(resultado)

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

        json_data = {

            "chat_id": CHAT_ID,

            "text": texto

        }

        if reply_markup:

            json_data[
                "reply_markup"
            ] = reply_markup.to_dict()

        response = requests.post(

            f"https://api.telegram.org/bot{TOKEN}/sendMessage",

            json=json_data

        )