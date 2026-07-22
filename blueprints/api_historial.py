# ==========================================
# BLUEPRINTS / API_HISTORIAL.PY
# Últimos 50 viajes, para la vista de historial
# ==========================================
from flask import Blueprint, jsonify
import state
from database import cursor

api_historial_bp = Blueprint("api_historial", __name__)


@api_historial_bp.route("/api/historial")
def api_historial():
    with state.STATE_LOCK:
        cursor.execute("""
            SELECT id, fecha, tipo_viaje, dinero, distancia_total,
                   tiempo_total, score_visual, estado, motivo_cancelacion
            FROM viajes
            ORDER BY fecha DESC
            LIMIT 50
        """)
        rows = cursor.fetchall()
        viajes = []
        for r in rows:
            viajes.append({
                "id": r[0],
                "fecha": r[1],
                "tipo_viaje": r[2],
                "dinero": r[3],
                "distancia_total": round(r[4] or 0, 2),
                "tiempo_total": r[5],
                "score_visual": r[6],
                "estado": r[7],
                "motivo_cancelacion": r[8]
            })
        return jsonify(viajes)
