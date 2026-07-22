# ==========================================
# BLUEPRINTS / API_INICIO.PY
# Dashboard principal: stats de hoy + últimos viajes
# ==========================================
from flask import Blueprint, jsonify
import state
from database import cursor

api_inicio_bp = Blueprint("api_inicio", __name__)


@api_inicio_bp.route("/api/inicio")
def api_inicio():
    with state.STATE_LOCK:
        cursor.execute("""
            SELECT COUNT(*) FROM viajes
            WHERE DATE(fecha) = DATE('now', '-5 hours')
        """)
        total_hoy = cursor.fetchone()[0]

        cursor.execute("""
            SELECT COUNT(*) FROM viajes WHERE estado='completado'
            AND DATE(fecha) = DATE('now', '-5 hours')
        """)
        completados_hoy = cursor.fetchone()[0]

        cursor.execute("""
            SELECT SUM(dinero) FROM viajes WHERE estado='completado'
            AND DATE(fecha) = DATE('now', '-5 hours')
        """)
        ganancia_hoy = cursor.fetchone()[0] or 0

        cursor.execute("""
            SELECT AVG(score_visual) FROM viajes WHERE estado='completado'
            AND DATE(fecha) = DATE('now', '-5 hours')
        """)
        score_prom = cursor.fetchone()[0] or 0

        cursor.execute("""
            SELECT SUM(distancia_total) FROM viajes WHERE estado='completado'
            AND DATE(fecha) = DATE('now', '-5 hours')
        """)
        km_total = cursor.fetchone()[0] or 0

        cursor.execute("SELECT COUNT(*) FROM viajes")
        total_db = cursor.fetchone()[0]

        cursor.execute("""
            SELECT id, fecha, dinero, distancia_total,
                   tiempo_total, score_visual, estado, motivo_cancelacion
            FROM viajes ORDER BY fecha DESC LIMIT 3
        """)
        rows = cursor.fetchall()
        ultimos = [{
            "id": r[0], "fecha": r[1], "dinero": r[2],
            "distancia_total": round(r[3] or 0, 2), "tiempo_total": r[4],
            "score_visual": r[5], "estado": r[6], "motivo_cancelacion": r[7]
        } for r in rows]

        return jsonify({
            "stats": {
                "ganancia": ganancia_hoy,
                "viajes": total_hoy,
                "completados": completados_hoy,
                "score_prom": round(score_prom, 1),
                "km_total": round(km_total, 1),
                "total_db": total_db
            },
            "ultimos_viajes": ultimos
        })
