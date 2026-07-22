# ==========================================
# BLUEPRINTS / API_OPERATIVO.PY
# Estado en vivo del viaje: nuevo / en curso / pendiente
# ==========================================
from flask import Blueprint, jsonify, request, redirect
import state
from database import actualizar_estado

api_operativo_bp = Blueprint("api_operativo", __name__)


# ==========================================
# API — ESTADO PARA OPERATIVO (polling)
# ==========================================
@api_operativo_bp.route("/api/operativo")
def api_operativo():
    with state.STATE_LOCK:
        return jsonify({
            "viaje_nuevo": state.viaje_nuevo,
            "viaje_en_curso": state.viaje_en_curso,
            "viaje_pendiente": state.viaje_pendiente
        })


# ==========================================
# ACEPTAR VIAJE NUEVO
# ==========================================
@api_operativo_bp.route("/web/aceptar")
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
@api_operativo_bp.route("/web/rechazar")
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
@api_operativo_bp.route("/web/finalizar")
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
@api_operativo_bp.route("/web/cancelar/usuario")
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
@api_operativo_bp.route("/web/cancelar/conductor")
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
