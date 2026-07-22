from flask import jsonify, request
import state
from database import cursor, conn, actualizar_estado

def registrar_api(app):

    # ==========================================
    # ESTADO JSON
    # ==========================================
    @app.route("/estado")
    def estado():
        return jsonify({
            "viaje_en_curso": state.viaje_en_curso,
            "viaje_pendiente": state.viaje_pendiente,
            "vista_actual": state.vista_actual
        })

    # ==========================================
    # API — GET CONFIG
    # ==========================================
    @app.route("/api/config")
    def api_config_get():
        from fuel import obtener_config, calcular_costo_km, calcular_gasto_combustible_total, calcular_combustible_restante
        km_l = obtener_config("km_l")
        valor_galon = obtener_config("valor_galon")
        tanque = obtener_config("tanque")
        costo_km = calcular_costo_km()
        gasto_total = calcular_gasto_combustible_total()
        restante = calcular_combustible_restante()
        return jsonify({
            "km_l": km_l,
            "valor_galon": valor_galon,
            "tanque": tanque,
            "costo_km": costo_km,
            "gasto_total": gasto_total,
            "restante": restante
        })

    # ==========================================
    # API — GUARDAR CONFIG
    # ==========================================
    @app.route("/api/config", methods=["POST"])
    def api_config_post():
        from fuel import guardar_config
        data = request.get_json()
        clave = data.get("clave")
        valor = data.get("valor")
        if not clave or valor is None:
            return jsonify({"error": "Faltan datos"}), 400
        if clave not in ("km_l", "valor_galon", "tanque"):
            return jsonify({"error": "Clave inválida"}), 400
        try:
            guardar_config(clave, float(valor))
            return jsonify({"success": True})
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    # ==========================================
    # API — BORRAR HISTORIAL COMPLETO
    # ==========================================
    @app.route("/api/borrar-historial", methods=["POST"])
    def api_borrar_historial():
        with state.STATE_LOCK:
            cursor.execute("DELETE FROM viajes")
            conn.commit()
            state.viaje_nuevo = None
            state.viaje_en_curso = None
            state.viaje_pendiente = None
        return jsonify({"success": True})

    # ==========================================
    # API — REINICIAR DÍA
    # ==========================================
    @app.route("/api/reiniciar-dia", methods=["POST"])
    def api_reiniciar_dia():
        from database import borrar_dia
        from datetime import datetime
        import pytz
        zona_colombia = pytz.timezone("America/Bogota")
        hoy = datetime.now(zona_colombia).strftime("%Y-%m-%d")
        borrar_dia(hoy)
        with state.STATE_LOCK:
            state.viaje_nuevo = None
            state.viaje_en_curso = None
            state.viaje_pendiente = None
        return jsonify({"success": True})