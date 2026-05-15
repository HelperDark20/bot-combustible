from flask import jsonify
import state
from flask import render_template

def registrar_api(app):

    @app.route("/estado")

    def estado():

        return jsonify({

            "viaje_en_curso":
                state.viaje_en_curso,

            "viaje_pendiente":
                state.viaje_pendiente,

            "vista_actual":
                state.vista_actual

        })  
    @app.route("/overlay")

    def overlay():

        viaje = state.viaje_pendiente or state.viaje_en_curso
        print(viaje)

        if not viaje:

            return "No hay viaje"

        pickup = viaje.get(
            "distancia_recogida_km",
            0
        )

        trayecto = viaje.get(
            "distancia_destino_km",
            0
        )

        total = pickup + trayecto

        if total > 0:

            porcentaje_usuario = int(
                (pickup / total) * 100
            )

        else:

            porcentaje_usuario = 50

        viaje["porcentaje_usuario"] = porcentaje_usuario

        viaje["distancia_total"] = round(

            viaje.get(
                "distancia_total",
                0
            ),

            1

        )

        dinero_por_km = float(

            viaje.get(
                "dinero_por_km",
                0
            ) or 0

        )

        dinero_por_min = float(

            viaje.get(
                "dinero_por_min",
                0
            ) or 0

        )

        viaje["dinero_por_km_texto"] = format(

            round(dinero_por_km),

            ","

        ).replace(",", ".")

        viaje["dinero_por_min_texto"] = format(

            round(dinero_por_min),

            ","

        ).replace(",", ".")

        ganancia = float(

            viaje.get(
                "ganancia",
                0
            ) or 0

        )

        viaje["ganancia"] = format(

            round(ganancia),

            ","

        ).replace(",", ".")

        dinero_por_km = float(

            viaje.get(
                "dinero_por_km",
                0
            ) or 0

        )

        viaje["dinero_por_km"] = format(

            round(dinero_por_km),

            ","

        ).replace(",", ".")

        dinero_por_min = float(

            viaje.get(
                "dinero_por_min",
                0
            ) or 0

        )

        viaje["dinero_por_min"] = format(

            round(dinero_por_min),

            ","

        ).replace(",", ".")

        return render_template(

            "overlay.html",

            viaje=viaje

        )
