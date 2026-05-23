# ==========================================
# IMPORTS
# ==========================================
from api import registrar_api
import uuid
import state
from score import construir_respuesta

from flask import Flask, request, jsonify, send_from_directory
from ocr import analizar_imagen_openai
from database import guardar_viaje
from ui_operativa import render_operativo
from config import TOKEN, CHAT_ID, VAPID_PUBLIC_KEY
from push_service import agregar_subscription, enviar_push

import requests
import json
import threading

# ==========================================
# FLASK
# ==========================================
flask_app = Flask(__name__)

# ==========================================
# API
# ==========================================
registrar_api(flask_app)

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
# PROCESAMIENTO EN BACKGROUND
# ==========================================
def procesar_y_notificar(data, viaje_id, resultado_score):
    try:
        nuevo_viaje = {
            "id": viaje_id,
            "ganancia": float(data["dinero"]),
            "distancia_recogida_km": float(data.get("distancia_recogida_km", 0)),
            "distancia_destino_km": float(data.get("distancia_destino_km", 0)),
            "distancia_total": resultado_score["distancia_total"],
            "tiempo_total": resultado_score["tiempo_total"],
            "dinero_por_km": resultado_score["dinero_por_km"],
            "dinero_por_min": resultado_score["dinero_por_min"],
            "dinero_por_hora": resultado_score["dinero_por_hora"],
            "score_visual": resultado_score["score_visual"],
            "estado_score": resultado_score["estado_score"],
        }

        with state.STATE_LOCK:
            state.viaje_nuevo = nuevo_viaje

        # ======================================
        # PUSH
        # ======================================
        km_fmt = f"{resultado_score['dinero_por_km']:,.0f}".replace(",", ".")
        dinero_hora_fmt = f"{int(resultado_score['dinero_por_hora']):,}".replace(",", ".")
        dinero_min_fmt = f"{int(resultado_score['dinero_por_min']):,}".replace(",", ".")
        distancia_total_fmt = f"{int(resultado_score['distancia_total']):,}".replace(",", ".")
        score = resultado_score["score_visual"]

        enviar_push({
            "title": f"🚘 Viaje — 💰{dinero_hora_fmt}/Hr · 💸{dinero_min_fmt}/Min",
            "body": f"⭐{score}/10 · 📍{distancia_total_fmt}Km · ⏱{resultado_score['tiempo_total']}Min · 💵{km_fmt}/Km",
            "url": "/operativo"
        })

        # ======================================
        # TELEGRAM
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

    except Exception as e:
        import traceback
        print(f"🔥 ERROR BACKGROUND: {e}")
        traceback.print_exc()

def procesar_imagen(ruta):
    try:
        respuesta_gpt = analizar_imagen_openai(ruta)
        respuesta_gpt = respuesta_gpt.replace("```json", "").replace("```", "").strip()
        data = json.loads(respuesta_gpt)

        # Normalizar tipo_viaje
        tipo_raw = data.get("tipo_viaje", "").lower()
        if "economy" in tipo_raw:
            data["tipo_viaje"] = "Economy"
        elif "comfort" in tipo_raw or "confort" in tipo_raw:
            data["tipo_viaje"] = "Comfort"
        elif "priority" in tipo_raw:
            data["tipo_viaje"] = "Priority"
        elif "xl" in tipo_raw:
            data["tipo_viaje"] = "UberXL"
        elif "black" in tipo_raw:
            data["tipo_viaje"] = "Black"
        else:
            data["tipo_viaje"] = "Economy"

        viaje_id = guardar_viaje(data)
        resultado_score = construir_respuesta(data)
        procesar_y_notificar(data, viaje_id, resultado_score)
    except Exception as e:
        import traceback
        print(f"🔥 ERROR IMAGEN: {e}")
        traceback.print_exc()

def procesar_texto(texto):
    try:
        from config import client
        respuesta = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "Extrae datos Uber Driver del texto. Solo JSON puro, sin markdown ni explicaciones."
                },
                {
                    "role": "user",
                    "content": f"""Extrae estos campos y devuelve solo JSON:
{{
  "tipo_viaje": "",
  "dinero": 0,
  "distancia_recogida_km": 0,
  "distancia_destino_km": 0,
  "tiempo_recogida_min": 0,
  "tiempo_destino_min": 0
}}

Texto de Uber Driver:
{texto}"""
                }
            ],
            max_tokens=120
        )
        contenido = respuesta.choices[0].message.content
        contenido = contenido.replace("```json", "").replace("```", "").strip()
        data = json.loads(contenido)

        # Normalizar tipo_viaje
        tipo_raw = data.get("tipo_viaje", "").lower()
        if "economy" in tipo_raw:
            data["tipo_viaje"] = "Economy"
        elif "comfort" in tipo_raw or "confort" in tipo_raw:
            data["tipo_viaje"] = "Comfort"
        elif "priority" in tipo_raw:
            data["tipo_viaje"] = "Priority"
        elif "xl" in tipo_raw:
            data["tipo_viaje"] = "UberXL"
        elif "black" in tipo_raw:
            data["tipo_viaje"] = "Black"
        else:
            data["tipo_viaje"] = "Economy"

        viaje_id = guardar_viaje(data)
        resultado_score = construir_respuesta(data)
        procesar_y_notificar(data, viaje_id, resultado_score)
    except Exception as e:
        import traceback
        print(f"🔥 ERROR TEXTO: {e}")
        traceback.print_exc()

# ==========================================
# UPLOAD TEXT — OCR nativo iOS
# ==========================================
@flask_app.route("/upload-text", methods=["POST"])
def upload_text():
    try:
        data_json = request.get_json()
        if not data_json or "texto" not in data_json:
            return jsonify({"error": "No text"}), 400
        thread = threading.Thread(target=procesar_texto, args=(data_json["texto"],), daemon=True)
        thread.start()
        return jsonify({"success": True})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

# ==========================================
# UPLOAD IMAGE
# ==========================================
@flask_app.route("/upload", methods=["POST"])
def upload():
    try:
        if "file" not in request.files:
            return jsonify({"error": "No image"}), 400
        image = request.files["file"]
        ruta = f"{uuid.uuid4()}.jpg"
        image.save(ruta)
        thread = threading.Thread(target=procesar_imagen, args=(ruta,), daemon=True)
        thread.start()
        return jsonify({"success": True})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

# ==========================================
# PUSH TEST
# ==========================================
@flask_app.route("/push/test")
def push_test():
    try:
        enviar_push({
            "title": "🧪 Test push",
            "body": "Si ves esto funciona!",
            "url": "/operativo"
        })
        return "Push enviado, revisa el iPhone"
    except Exception as e:
        import traceback
        return traceback.format_exc(), 500

# ==========================================
# ICONOS APPLE
# ==========================================
@flask_app.route("/apple-touch-icon.png")
def apple_touch_icon():
    return send_from_directory("static", "icon-192.png")

@flask_app.route("/apple-touch-icon-120x120.png")
def apple_touch_icon_120():
    return send_from_directory("static", "icon-192.png")

@flask_app.route("/apple-touch-icon-120x120-precomposed.png")
def apple_touch_icon_120_pre():
    return send_from_directory("static", "icon-192.png")