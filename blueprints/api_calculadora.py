# ==========================================
# BLUEPRINTS / API_CALCULADORA.PY
# Módulo calculadora — 100% independiente
# de la tabla `configuracion`
# ==========================================
from flask import Blueprint, request, jsonify
import state
from database import cursor
from fuel import calcular_costo_km_manual
from score import calcular_score

api_calculadora_bp = Blueprint("api_calculadora", __name__, url_prefix="/api/calculadora")


# ==========================================
# TANQUEADA → KM POSIBLES
# ==========================================
@api_calculadora_bp.route("/tanqueada", methods=["POST"])
def tanqueada():
    data = request.get_json(silent=True) or {}

    try:
        monto = float(data.get("monto", 0))
        km_l = float(data.get("km_l", 0))
        valor_galon = float(data.get("valor_galon", 0))
    except (TypeError, ValueError):
        return jsonify({"error": "Datos inválidos"}), 400

    if monto <= 0 or km_l <= 0 or valor_galon <= 0:
        return jsonify({"error": "Completa todos los campos"}), 400

    costo_km = calcular_costo_km_manual(km_l, valor_galon)
    if costo_km <= 0:
        return jsonify({"error": "Datos de combustible inválidos"}), 400

    return jsonify({
        "km_posibles": round(monto / costo_km, 1),
        "costo_km": costo_km
    })


# ==========================================
# EVALUAR VIAJE MANUAL
# ==========================================
@api_calculadora_bp.route("/evaluar", methods=["POST"])
def evaluar():
    data = request.get_json(silent=True) or {}

    try:
        ganancia = float(data.get("ganancia", 0))
        distancia_total = float(data.get("distancia_total", 0))
        tiempo_total = float(data.get("tiempo_total", 0))
        km_l = float(data.get("km_l", 0))
        valor_galon = float(data.get("valor_galon", 0))
    except (TypeError, ValueError):
        return jsonify({"error": "Datos inválidos"}), 400

    if ganancia <= 0 or distancia_total <= 0 or km_l <= 0 or valor_galon <= 0:
        return jsonify({"error": "Completa todos los campos"}), 400

    datos = {
        "tipo_viaje": "Manual",
        "dinero": ganancia,
        "distancia_recogida_km": distancia_total,
        "distancia_destino_km": 0,
        "tiempo_recogida_min": tiempo_total,
        "tiempo_destino_min": 0
    }

    (_, _, dinero_por_km, dinero_por_min,
     score_visual, estado_score) = calcular_score(datos)

    costo_km = calcular_costo_km_manual(km_l, valor_galon)
    gasto_combustible = round(distancia_total * costo_km, 0)
    ganancia_neta = round(ganancia - gasto_combustible, 0)
    dinero_por_hora = round(dinero_por_min * 60, 0) if tiempo_total > 0 else 0

    return jsonify({
        "dinero_por_km": dinero_por_km,
        "dinero_por_min": dinero_por_min,
        "dinero_por_hora": dinero_por_hora,
        "score_visual": score_visual,
        "estado_score": estado_score,
        "gasto_combustible": gasto_combustible,
        "ganancia_neta": ganancia_neta
    })


# ==========================================
# META DEL DÍA
# ==========================================
@api_calculadora_bp.route("/meta", methods=["POST"])
def meta():
    data = request.get_json(silent=True) or {}

    try:
        meta_valor = float(data.get("meta", 0))
        km_l = float(data.get("km_l", 0))
        valor_galon = float(data.get("valor_galon", 0))
    except (TypeError, ValueError):
        return jsonify({"error": "Datos inválidos"}), 400

    if meta_valor <= 0 or km_l <= 0 or valor_galon <= 0:
        return jsonify({"error": "Completa todos los campos"}), 400

    with state.STATE_LOCK:
        cursor.execute("""
            SELECT COUNT(*) FROM viajes WHERE estado='completado'
            AND DATE(fecha) = DATE('now', '-5 hours')
        """)
        completados = cursor.fetchone()[0]

        cursor.execute("""
            SELECT SUM(dinero) FROM viajes WHERE estado='completado'
            AND DATE(fecha) = DATE('now', '-5 hours')
        """)
        ganancia_hoy = cursor.fetchone()[0] or 0

        cursor.execute("""
            SELECT SUM(distancia_total) FROM viajes WHERE estado='completado'
            AND DATE(fecha) = DATE('now', '-5 hours')
        """)
        km_hoy = cursor.fetchone()[0] or 0

    costo_km = calcular_costo_km_manual(km_l, valor_galon)
    gasto_hoy = round(km_hoy * costo_km, 0)
    neta_hoy = round(ganancia_hoy - gasto_hoy, 0)
    restante = round(meta_valor - neta_hoy, 0)
    promedio_neto = round(neta_hoy / completados, 0) if completados > 0 else 0

    return jsonify({
        "neta_hoy": neta_hoy,
        "restante": restante,
        "promedio_neto": promedio_neto,
        "completados": completados
    })
