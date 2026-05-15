# ==========================================
# IMPORTS
# ==========================================
from PIL import Image
import uuid
import base64
from config import client

# ==========================================
# OPTIMIZAR IMAGEN
# ==========================================
def optimizar_imagen(ruta_original):

    img = Image.open(ruta_original)

    width, height = img.size

    # ======================================
    # RECORTE INTELIGENTE
    # ======================================

    left = int(width * 0.10)

    top = int(height * 0.30)

    right = int(width * 0.90)

    bottom = int(height * 1.00)

    crop = img.crop(
        (left, top, right, bottom)
    )

    # ======================================
    # REDUCIR TAMAÑO
    # ======================================

    crop.thumbnail((700, 700))

    ruta_final = f"{uuid.uuid4()}.jpg"

    if crop.mode in ("RGBA", "P"):
        crop = crop.convert("RGB")

    crop.save(

        ruta_final,

        optimize=True,

        quality=35
    )

    return ruta_final

# ==========================================
# GPT VISION
# ==========================================
def analizar_imagen_openai(ruta_imagen):

    ruta_imagen = optimizar_imagen(
        ruta_imagen
    )

    with open(ruta_imagen, "rb") as img_file:

        base64_image = base64.b64encode(
            img_file.read()
        ).decode("utf-8")

    try:

        respuesta = client.chat.completions.create(

            model="gpt-4o-mini",

            messages=[

                {
                    "role": "system",

                    "content":
                        "Extrae datos Uber Driver. Solo JSON."
                },

                {
                    "role": "user",

                    "content": [

                        {
                            "type": "text",

                            "text":

                            """
                            {
                            "tipo_viaje":"",
                            "dinero":0,
                            "distancia_recogida_km":0,
                            "distancia_destino_km":0,
                            "tiempo_recogida_min":0,
                            "tiempo_destino_min":0
                            }
                            """
                        },

                        {
                            "type": "image_url",

                            "image_url": {

                                "url":
                                f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],

            max_tokens=90
        )

    except Exception as e:

        print(
            f"🔥 OCR ERROR: {e}"
        )

        return None

    contenido = (

        respuesta
        .choices[0]
        .message
        .content
    )

    return contenido