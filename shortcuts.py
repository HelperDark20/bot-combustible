# ==========================================
# IMPORTS
# ==========================================
from flask import (

    Flask,
    request,
    jsonify
)

from telegram_ui import botones_pendiente

from ocr import analizar_imagen_openai

from database import guardar_viaje

from score import construir_respuesta

from config import (

    TOKEN,
    CHAT_ID
)

from telegram import InlineKeyboardMarkup

import requests
import json

# ==========================================
# FLASK
# ==========================================
flask_app = Flask(__name__)

# ==========================================
# HOME
# ==========================================
@flask_app.route("/")
def home():

    return "BOT IA VIAJES ACTIVO"

# ==========================================
# UPLOAD SHORTCUTS
# ==========================================
@flask_app.route(

    "/upload",

    methods=["POST"]
)

def upload():

    try:

        # ==================================
        # VALIDAR IMAGEN
        # ==================================

        print("FILES:", request.files)
        print("FORM:", request.form)

        if "file" not in request.files:

            return jsonify({
                "error": "No image"
            }), 400

        # ==================================
        # GUARDAR IMAGEN
        # ==================================

        image = request.files["file"]

        ruta = "shortcut.jpg"

        image.save(ruta)

        # ==================================
        # GPT VISION
        # ==================================

        respuesta_gpt = analizar_imagen_openai(
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

        # ==================================
        # GUARDAR VIAJE
        # ==================================

        viaje_id = guardar_viaje(data)

        # ==================================
        # RESPUESTA
        # ==================================

        respuesta = construir_respuesta(
            data
        )

        # ==================================
        # BOTONES
        # ==================================

        reply_markup = botones_pendiente(
            viaje_id
        )

        # ==================================
        # ENVIAR TELEGRAM
        # ==================================

        requests.post(

            f"https://api.telegram.org/bot{TOKEN}/sendMessage",

            json={

                "chat_id": CHAT_ID,

                "text":
                    "📲 VIA SHORTCUTS\n\n"
                    + respuesta,

                "reply_markup":
                    reply_markup.to_dict()
            }
        )

        return jsonify({
            "success": True
        })

    except Exception as e:

        print(e)

        return jsonify({
            "error": str(e)
        }), 500