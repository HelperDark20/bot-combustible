from flask import jsonify, render_template, redirect, request
import state
from database import cursor, conn, actualizar_estado
from config import VAPID_PUBLIC_KEY
import sqlite3

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
    # HOME → inicio
    # ==========================================
    @app.route("/")
    def home():
        return render_template("inicio.html")

    @app.route("/inicio")
    def inicio():
        return render_template("inicio.html")

    # ==========================================
    # API — INICIO (stats hoy + últimos 3 viajes)
    # ==========================================
    @app.route("/api/inicio")
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
                "distancia_total": r[3], "tiempo_total": r[4],
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

    # ==========================================
    # OPERATIVO
    # ==========================================
    @app.route("/operativo")
    def operativo():
        return render_template(
            "operativo.html",
            vapid_public_key=VAPID_PUBLIC_KEY
        )

    # ==========================================
    # OVERLAY
    # ==========================================
    @app.route("/overlay")
    def overlay():
        viaje_original = state.viaje_pendiente or state.viaje_en_curso
        if not viaje_original:
            return redirect("/operativo")

        viaje = viaje_original.copy()
        pickup = float(viaje.get("distancia_recogida_km", 0))
        trayecto = float(viaje.get("distancia_destino_km", 0))
        total = pickup + trayecto

        viaje["porcentaje_usuario"] = int((pickup / total) * 100) if total > 0 else 50
        viaje["distancia_total"] = round(float(viaje.get("distancia_total", 0)), 1)

        dinero_por_km = float(viaje.get("dinero_por_km", 0) or 0)
        dinero_por_min = float(viaje.get("dinero_por_min", 0) or 0)

        viaje["dinero_por_km_texto"] = format(round(dinero_por_km), ",").replace(",", ".")
        viaje["dinero_por_min_texto"] = format(round(dinero_por_min), ",").replace(",", ".")
        viaje["dinero_por_hora_texto"] = format(round(dinero_por_min * 60), ",").replace(",", ".")
        viaje["ganancia"] = format(round(float(viaje.get("ganancia", 0) or 0)), ",").replace(",", ".")

        return render_template("overlay.html", viaje=viaje, vapid_public_key=VAPID_PUBLIC_KEY)

    # ==========================================
    # PUSH REGISTER
    # ==========================================
    @app.route("/push/register")
    def push_register():
        return render_template("push_register.html", vapid_public_key=VAPID_PUBLIC_KEY)

    # ==========================================
    # ACEPTAR VIAJE
    # ==========================================
    @app.route("/web/aceptar")
    def web_aceptar():
        with state.STATE_LOCK:
            if state.viaje_nuevo:
                if state.viaje_en_curso:
                    # Si hay uno en curso, el nuevo pasa a pendiente
                    state.viaje_pendiente = state.viaje_nuevo.copy()
                else:
                    state.viaje_en_curso = state.viaje_nuevo.copy()

                viaje_id = state.viaje_nuevo.get("id")
                if viaje_id:
                    actualizar_estado(viaje_id, "iniciado")

                state.viaje_nuevo = None

        return redirect("/operativo")

    # ==========================================
    # RECHAZAR VIAJE NUEVO
    # ==========================================
    @app.route("/web/rechazar")
    def web_rechazar():
        with state.STATE_LOCK:
            if state.viaje_nuevo:
                viaje_id = state.viaje_nuevo.get("id")
                if viaje_id:
                    actualizar_estado(viaje_id, "rechazado")
                state.viaje_nuevo = None

        return redirect("/operativo")

    # ==========================================
    # FINALIZAR VIAJE EN CURSO
    # ==========================================
    @app.route("/web/finalizar")
    def web_finalizar():
        with state.STATE_LOCK:
            if state.viaje_en_curso:
                viaje_id = state.viaje_en_curso.get("id")
                if viaje_id:
                    actualizar_estado(viaje_id, "completado")

                if state.viaje_pendiente:
                    state.viaje_en_curso = state.viaje_pendiente.copy()
                    state.viaje_pendiente = None
                else:
                    state.viaje_en_curso = None

        return redirect("/operativo")

    # ==========================================
    # CANCELAR — USUARIO (en curso o pendiente)
    # ==========================================
    @app.route("/web/cancelar/usuario")
    def web_cancelar_usuario():
        with state.STATE_LOCK:
            tipo = request.args.get("tipo", "curso")

            if tipo == "pendiente" and state.viaje_pendiente:
                viaje_id = state.viaje_pendiente.get("id")
                if viaje_id:
                    actualizar_estado(viaje_id, "cancelado_usuario", "Cancelado por usuario")
                state.viaje_pendiente = None

            elif state.viaje_en_curso:
                viaje_id = state.viaje_en_curso.get("id")
                if viaje_id:
                    actualizar_estado(viaje_id, "cancelado_usuario", "Cancelado por usuario")

                if state.viaje_pendiente:
                    state.viaje_en_curso = state.viaje_pendiente.copy()
                    state.viaje_pendiente = None
                else:
                    state.viaje_en_curso = None

        return redirect("/operativo")

    # ==========================================
    # CANCELAR — CONDUCTOR (en curso o pendiente)
    # ==========================================
    @app.route("/web/cancelar/conductor")
    def web_cancelar_conductor():
        with state.STATE_LOCK:
            tipo = request.args.get("tipo", "curso")

            if tipo == "pendiente" and state.viaje_pendiente:
                viaje_id = state.viaje_pendiente.get("id")
                if viaje_id:
                    actualizar_estado(viaje_id, "cancelado_conductor", "Cancelado por conductor")
                state.viaje_pendiente = None

            elif state.viaje_en_curso:
                viaje_id = state.viaje_en_curso.get("id")
                if viaje_id:
                    actualizar_estado(viaje_id, "cancelado_conductor", "Cancelado por conductor")

                if state.viaje_pendiente:
                    state.viaje_en_curso = state.viaje_pendiente.copy()
                    state.viaje_pendiente = None
                else:
                    state.viaje_en_curso = None

        return redirect("/operativo")

    # ==========================================
    # API — ESTADO PARA OPERATIVO (polling)
    # ==========================================
    @app.route("/api/operativo")
    def api_operativo():
        with state.STATE_LOCK:
            return jsonify({
                "viaje_nuevo": state.viaje_nuevo,
                "viaje_en_curso": state.viaje_en_curso,
                "viaje_pendiente": state.viaje_pendiente
            })

    # ==========================================
    # API — STATS HOY
    # ==========================================
    @app.route("/api/stats/hoy")
    def api_stats_hoy():
        with state.STATE_LOCK:
            cursor.execute("""
                SELECT COUNT(*) FROM viajes
                WHERE DATE(fecha) = DATE('now', '-5 hours')
            """)
            total = cursor.fetchone()[0]

            cursor.execute("""
                SELECT COUNT(*) FROM viajes
                WHERE estado='completado'
                AND DATE(fecha) = DATE('now', '-5 hours')
            """)
            completados = cursor.fetchone()[0]

            cursor.execute("""
                SELECT COUNT(*) FROM viajes
                WHERE estado IN ('cancelado_usuario','cancelado_conductor','rechazado')
                AND DATE(fecha) = DATE('now', '-5 hours')
            """)
            cancelados = cursor.fetchone()[0]

            cursor.execute("""
                SELECT SUM(dinero) FROM viajes
                WHERE estado='completado'
                AND DATE(fecha) = DATE('now', '-5 hours')
            """)
            ganancia = cursor.fetchone()[0] or 0

            cursor.execute("""
                SELECT AVG(score_visual) FROM viajes
                WHERE estado='completado'
                AND DATE(fecha) = DATE('now', '-5 hours')
            """)
            score_prom = cursor.fetchone()[0] or 0

            cursor.execute("""
                SELECT SUM(distancia_total) FROM viajes
                WHERE estado='completado'
                AND DATE(fecha) = DATE('now', '-5 hours')
            """)
            km_total = cursor.fetchone()[0] or 0

            return jsonify({
                "total": total,
                "completados": completados,
                "cancelados": cancelados,
                "ganancia": ganancia,
                "score_prom": round(score_prom, 1),
                "km_total": round(km_total, 1)
            })

    # ==========================================
    # API — STATS SEMANA
    # ==========================================
    @app.route("/api/stats/semana")
    def api_stats_semana():
        with state.STATE_LOCK:
            cursor.execute("""
                SELECT COUNT(*) FROM viajes
                WHERE strftime('%W', fecha) = strftime('%W', 'now', '-5 hours')
            """)
            total = cursor.fetchone()[0]

            cursor.execute("""
                SELECT COUNT(*) FROM viajes WHERE estado='completado'
                AND strftime('%W', fecha) = strftime('%W', 'now', '-5 hours')
            """)
            completados = cursor.fetchone()[0]

            cursor.execute("""
                SELECT COUNT(*) FROM viajes
                WHERE estado IN ('cancelado_usuario','cancelado_conductor','rechazado')
                AND strftime('%W', fecha) = strftime('%W', 'now', '-5 hours')
            """)
            cancelados = cursor.fetchone()[0]

            cursor.execute("""
                SELECT SUM(dinero) FROM viajes WHERE estado='completado'
                AND strftime('%W', fecha) = strftime('%W', 'now', '-5 hours')
            """)
            ganancia = cursor.fetchone()[0] or 0

            cursor.execute("""
                SELECT AVG(score_visual) FROM viajes WHERE estado='completado'
                AND strftime('%W', fecha) = strftime('%W', 'now', '-5 hours')
            """)
            score_prom = cursor.fetchone()[0] or 0

            cursor.execute("""
                SELECT SUM(distancia_total) FROM viajes WHERE estado='completado'
                AND strftime('%W', fecha) = strftime('%W', 'now', '-5 hours')
            """)
            km_total = cursor.fetchone()[0] or 0

            return jsonify({
                "total": total,
                "completados": completados,
                "cancelados": cancelados,
                "ganancia": ganancia,
                "score_prom": round(score_prom, 1),
                "km_total": round(km_total, 1)
            })

    # ==========================================
    # API — STATS MES
    # ==========================================
    @app.route("/api/stats/mes")
    def api_stats_mes():
        with state.STATE_LOCK:
            cursor.execute("""
                SELECT COUNT(*) FROM viajes
                WHERE strftime('%m%Y', fecha) = strftime('%m%Y', 'now', '-5 hours')
            """)
            total = cursor.fetchone()[0]

            cursor.execute("""
                SELECT COUNT(*) FROM viajes WHERE estado='completado'
                AND strftime('%m%Y', fecha) = strftime('%m%Y', 'now', '-5 hours')
            """)
            completados = cursor.fetchone()[0]

            cursor.execute("""
                SELECT COUNT(*) FROM viajes
                WHERE estado IN ('cancelado_usuario','cancelado_conductor','rechazado')
                AND strftime('%m%Y', fecha) = strftime('%m%Y', 'now', '-5 hours')
            """)
            cancelados = cursor.fetchone()[0]

            cursor.execute("""
                SELECT SUM(dinero) FROM viajes WHERE estado='completado'
                AND strftime('%m%Y', fecha) = strftime('%m%Y', 'now', '-5 hours')
            """)
            ganancia = cursor.fetchone()[0] or 0

            cursor.execute("""
                SELECT AVG(score_visual) FROM viajes WHERE estado='completado'
                AND strftime('%m%Y', fecha) = strftime('%m%Y', 'now', '-5 hours')
            """)
            score_prom = cursor.fetchone()[0] or 0

            cursor.execute("""
                SELECT SUM(distancia_total) FROM viajes WHERE estado='completado'
                AND strftime('%m%Y', fecha) = strftime('%m%Y', 'now', '-5 hours')
            """)
            km_total = cursor.fetchone()[0] or 0

            return jsonify({
                "total": total,
                "completados": completados,
                "cancelados": cancelados,
                "ganancia": ganancia,
                "score_prom": round(score_prom, 1),
                "km_total": round(km_total, 1)
            })

    # ==========================================
    # API — STATS TOTAL
    # ==========================================
    @app.route("/api/stats/total")
    def api_stats_total():
        with state.STATE_LOCK:
            cursor.execute("SELECT COUNT(*) FROM viajes")
            total = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM viajes WHERE estado='completado'")
            completados = cursor.fetchone()[0]

            cursor.execute("""
                SELECT COUNT(*) FROM viajes
                WHERE estado IN ('cancelado_usuario','cancelado_conductor','rechazado')
            """)
            cancelados = cursor.fetchone()[0]

            cursor.execute("SELECT SUM(dinero) FROM viajes WHERE estado='completado'")
            ganancia = cursor.fetchone()[0] or 0

            cursor.execute("SELECT AVG(score_visual) FROM viajes WHERE estado='completado'")
            score_prom = cursor.fetchone()[0] or 0

            cursor.execute("SELECT SUM(distancia_total) FROM viajes WHERE estado='completado'")
            km_total = cursor.fetchone()[0] or 0

            return jsonify({
                "total": total,
                "completados": completados,
                "cancelados": cancelados,
                "ganancia": ganancia,
                "score_prom": round(score_prom, 1),
                "km_total": round(km_total, 1)
            })

    # ==========================================
    # API — HISTORIAL (últimos 50)
    # ==========================================
    @app.route("/api/historial")
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
                    "distancia_total": r[4],
                    "tiempo_total": r[5],
                    "score_visual": r[6],
                    "estado": r[7],
                    "motivo_cancelacion": r[8]
                })
            return jsonify(viajes)