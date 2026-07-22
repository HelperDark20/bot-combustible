# ==========================================
# BLUEPRINTS / API_STATS.PY
# Estadísticas por período: hoy / semana / mes / total
# ==========================================
from flask import Blueprint, jsonify
import state
from database import cursor

api_stats_bp = Blueprint("api_stats", __name__, url_prefix="/api/stats")


def _stats_query(filtro_sql):
    """
    Ejecuta el bloque de queries compartido por los 4 períodos.
    filtro_sql: condición SQL ya armada (ej: "DATE(fecha) = DATE('now', '-5 hours')")
    """
    cursor.execute(f"SELECT COUNT(*) FROM viajes WHERE {filtro_sql}")
    total = cursor.fetchone()[0]

    cursor.execute(f"SELECT COUNT(*) FROM viajes WHERE estado='completado' AND {filtro_sql}")
    completados = cursor.fetchone()[0]

    cursor.execute(f"""
        SELECT COUNT(*) FROM viajes
        WHERE estado IN ('cancelado_usuario','cancelado_conductor') AND {filtro_sql}
    """)
    cancelados = cursor.fetchone()[0]

    cursor.execute(f"SELECT COUNT(*) FROM viajes WHERE estado='rechazado' AND {filtro_sql}")
    rechazados = cursor.fetchone()[0]

    cursor.execute(f"SELECT SUM(dinero) FROM viajes WHERE estado='completado' AND {filtro_sql}")
    ganancia = cursor.fetchone()[0] or 0

    cursor.execute(f"SELECT AVG(score_visual) FROM viajes WHERE estado='completado' AND {filtro_sql}")
    score_prom = cursor.fetchone()[0] or 0

    cursor.execute(f"SELECT SUM(distancia_total) FROM viajes WHERE estado='completado' AND {filtro_sql}")
    km_total = cursor.fetchone()[0] or 0

    return jsonify({
        "total": total,
        "completados": completados,
        "cancelados": cancelados,
        "rechazados": rechazados,
        "ganancia": ganancia,
        "score_prom": round(score_prom, 1),
        "km_total": round(km_total, 1)
    })


@api_stats_bp.route("/hoy")
def stats_hoy():
    with state.STATE_LOCK:
        return _stats_query("DATE(fecha) = DATE('now', '-5 hours')")


@api_stats_bp.route("/semana")
def stats_semana():
    with state.STATE_LOCK:
        return _stats_query("strftime('%W', fecha) = strftime('%W', 'now', '-5 hours')")


@api_stats_bp.route("/mes")
def stats_mes():
    with state.STATE_LOCK:
        return _stats_query("strftime('%m%Y', fecha) = strftime('%m%Y', 'now', '-5 hours')")


@api_stats_bp.route("/total")
def stats_total():
    with state.STATE_LOCK:
        return _stats_query("1=1")
