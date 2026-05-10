# ==========================================
# IMPORTS
# ==========================================
from state import (

    viaje_en_curso,
    viaje_pendiente,
    vista_actual,
    message_id_operativo

)

import state

from score import construir_respuesta

from flask import (

    Flask,
    request,
    jsonify
)

from ocr import analizar_imagen_openai

from database import guardar_viaje

from ui_operativa import (
    render_operativo
)

from config import (

    TOKEN,
    CHAT_ID
)

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
        # RESULTADO SCORE
        # ==================================

        resultado_score = construir_respuesta(
            data
        )

        # ==================================
        # NUEVO VIAJE OPERATIVO
        # ==================================

        nuevo_viaje = {
            
            "id": viaje_id,

            "ganancia": float(data["dinero"]),

            "distancia_total":
                resultado_score["distancia_total"],

            "tiempo_total":
                resultado_score["tiempo_total"],

            "dinero_por_km":
                resultado_score["dinero_por_km"],

            "dinero_por_min":
                resultado_score["dinero_por_min"],

            "score_visual":
                resultado_score["score_visual"],

            "estado_score":
                resultado_score["estado_score"],

            "estado_operativo":
                "curso" if not state.viaje_en_curso
                else "pendiente"

        }

        # ==================================
        # LÓGICA OPERATIVA
        # ==================================

        if state.viaje_en_curso:

            state.viaje_pendiente = nuevo_viaje

            state.vista_actual = "pendiente"

        else:

            state.viaje_en_curso = nuevo_viaje

            state.vista_actual = "curso"

        # ==================================
        # RENDER OPERATIVO
        # ==================================

        texto, reply_markup = render_operativo()

        # ==================================
        # ACTUALIZAR PANEL
        # ==================================

        if state.message_id_operativo:

            requests.post(

                f"https://api.telegram.org/bot{TOKEN}/editMessageText",

                json={

                    "chat_id": CHAT_ID,

                    "message_id":
                        state.message_id_operativo,

                    "text": texto,

                    "reply_markup":
                        reply_markup.to_dict()

                }
            )

        # ==================================
        # CREAR PANEL
        # ==================================

        else:

            response = requests.post(

                f"https://api.telegram.org/bot{TOKEN}/sendMessage",

                json={

                    "chat_id": CHAT_ID,

                    "text": texto,

                    "reply_markup":
                        reply_markup.to_dict()

                }
            )

            resultado = response.json()

            state.message_id_operativo = (

                resultado["result"]["message_id"]

            )

        return jsonify({
            "success": True
        })

    except Exception as e:
        import traceback
        traceback.print_exc()

        return jsonify({
            "error": str(e)
        }), 500