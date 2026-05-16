# ==========================================
# IMPORTS
# ==========================================

from api import registrar_api
import uuid
import state
from score import construir_respuesta

from flask import (
    Flask,
    request,
    jsonify,
    send_from_directory
)

from ocr import analizar_imagen_openai
from database import guardar_viaje
from ui_operativa import render_operativo

from config import (
    TOKEN,
    CHAT_ID,
    VAPID_PUBLIC_KEY
)

from push_service import (
    agregar_subscription,
    enviar_push
)

import requests
import json

# ==========================================
# FLASK
# ==========================================
flask_app = Flask(__name__)

# ==========================================
# API
# ==========================================
registrar_api(flask_app)

# ==========================================
# HOME
# ==========================================
@flask_app.route("/")
def home():
    return "BOT IA VIAJES ACTIVO"

# ==========================================
# PWA — manifest y service worker
# ==========================================
@flask_app.route("/manifest.json")
def manifest():
    return send_from_directory("static", "manifest.json")

@flask_app.route("/sw.js")
def service_worker():
    response = send_from_directory("static", "sw.js")
    response.headers["Cache-Control"] = "no-cache"
    response.headers["Content-Type"] = "application/javascript"
    return response

# ==========================================
# PUSH — suscribir dispositivo
# ==========================================
@flask_app.route("/push/subscribe", methods=["POST"])
def push_subscribe():
    try:
        sub = request.get_json()
        agregar_subscription(sub)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ==========================================
# PUSH — VAPID public key
# ==========================================
@flask_app.route("/push/vapid-key")
def push_vapid_key():
    return jsonify({"key": VAPID_PUBLIC_KEY})

# ==========================================
# UPLOAD
# ==========================================
@flask_app.route("/upload", methods=["POST"])
def upload():

    try:

        if "file" not in request.files:
            return jsonify({"error": "No image"}), 400

        image = request.files["file"]
        ruta = f"{uuid.uuid4()}.jpg"
        image.save(ruta)

        respuesta_gpt = analizar_imagen_openai(ruta)
        respuesta_gpt = (
            respuesta_gpt
            .replace("```json", "")
            .replace("```", "")
            .strip()
        )

        data = json.loads(respuesta_gpt)
        viaje_id = guardar_viaje(data)
        resultado_score = construir_respuesta(data)

        nuevo_viaje = {
            "id": viaje_id,
            "ganancia": float(data["dinero"]),
            "distancia_recogida_km": float(data.get("distancia_recogida_km", 0)),
            "distancia_destino_km": float(data.get("distancia_destino_km", 0)),
            "distancia_total": resultado_score["distancia_total"],
            "tiempo_total": resultado_score["tiempo_total"],
            "dinero_por_km": resultado_score["dinero_por_km"],
            "dinero_por_min": resultado_score["dinero_por_min"],
            "score_visual": resultado_score["score_visual"],
            "estado_score": resultado_score["estado_score"],
            "estado_operativo": "curso" if not state.viaje_en_curso else "pendiente"
        }

        if state.viaje_en_curso:
            state.viaje_pendiente = nuevo_viaje
            state.vista_actual = "pendiente"
        else:
            state.viaje_en_curso = nuevo_viaje
            state.vista_actual = "curso"

        # ======================================
        # ENVIAR PUSH NOTIFICATION
        # ======================================
        km_fmt = f"{resultado_score['dinero_por_km']:,.0f}".replace(",", ".")
        dinero_hora_fmt = f"{int(resultado_score['dinero_por_hora']):,}".replace(",", ".")
        score = resultado_score["score_visual"]

        try:
            print("🔔 LLAMANDO ENVIAR PUSH...")
            enviar_push({
                "title": f"🚘 Viaje — ${dinero_hora_fmt}/hr",
                "body": f"⭐{score}/10 · 📍{resultado_score['distancia_total']}KM · ⏱{resultado_score['tiempo_total']}MIN · 💵{km_fmt}/KM",
                "url": "/overlay"
            })
        except Exception as push_error:
            print(f"🔥 ERROR EN ENVIAR PUSH: {push_error}")
            import traceback
            traceback.print_exc()

        # ======================================
        # RENDER OPERATIVO TELEGRAM
        # ======================================
        texto, reply_markup = render_operativo()

        if state.message_id_operativo:
            requests.post(
                f"https://api.telegram.org/bot{TOKEN}/editMessageText",
                json={
                    "chat_id": CHAT_ID,
                    "message_id": state.message_id_operativo,
                    "text": texto,
                    "reply_markup": reply_markup.to_dict()
                },
                timeout=10
            )
        else:
            response = requests.post(
                f"https://api.telegram.org/bot{TOKEN}/sendMessage",
                json={
                    "chat_id": CHAT_ID,
                    "text": texto,
                    "reply_markup": reply_markup.to_dict()
                },
                timeout=10
            )
            resultado = response.json()
            state.message_id_operativo = resultado["result"]["message_id"]

        return jsonify({"success": True})

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500
    
@flask_app.route("/push/test")
def push_test():
    try:
        enviar_push({
            "title": "🧪 Test push",
            "body": "Si ves esto funciona!",
            "url": "/overlay"
        })
        return "Push enviado, revisa el iPhone"
    except Exception as e:
        import traceback
        return traceback.format_exc(), 500
@flask_app.route("/apple-touch-icon.png")
def apple_touch_icon():
    return send_from_directory("static", "icon-192.png")

@flask_app.route("/apple-touch-icon-120x120.png")
def apple_touch_icon_120():
    return send_from_directory("static", "icon-192.png")

@flask_app.route("/apple-touch-icon-120x120-precomposed.png")
def apple_touch_icon_120_pre():
    return send_from_directory("static", "icon-192.png")