# ==========================================
# BLUEPRINTS / PAGES.PY
# Rutas que renderizan HTML (no JSON)
# ==========================================
from flask import Blueprint, render_template, redirect
import state
from config import VAPID_PUBLIC_KEY

pages_bp = Blueprint("pages", __name__)


@pages_bp.route("/")
@pages_bp.route("/inicio")
def inicio():
    return render_template("inicio.html", active="inicio", page_title="Inicio")


@pages_bp.route("/operativo")
def operativo():
    return render_template("operativo.html", active="operativo", page_title="Operativo")


@pages_bp.route("/stats")
def stats():
    return render_template("stats.html", active="stats", page_title="Stats")


@pages_bp.route("/historial")
def historial():
    return render_template("historial.html", active="historial", page_title="Historial")


@pages_bp.route("/calculadora")
def calculadora():
    return render_template("calculadora.html", active="calculadora", page_title="Calculadora")


@pages_bp.route("/config")
def config():
    return render_template("config.html", active="config", page_title="Config")


@pages_bp.route("/overlay")
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


@pages_bp.route("/push/register")
def push_register():
    return render_template("push_register.html", vapid_public_key=VAPID_PUBLIC_KEY)
