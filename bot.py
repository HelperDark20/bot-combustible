# ==========================================
# IMPORTS
# ==========================================
import threading

from telegram.ext import (

    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters
)

from config import (

    TOKEN,
    PORT
)

from handlers import (

    start,
    botones_callback,
    recibir_imagen,
    recibir_texto,
    borrar_fecha
)

from shortcuts import flask_app

from fuel import (
    crear_tabla_config
)

# ==========================================
# CREAR TABLA CONFIG
# ==========================================
crear_tabla_config()

# ==========================================
# TELEGRAM
# ==========================================
telegram_app = (

    Application
    .builder()
    .token(TOKEN)
    .build()
)

# ==========================================
# HANDLERS
# ==========================================
telegram_app.add_handler(
    CommandHandler("start", start)
)

telegram_app.add_handler(
    CommandHandler(
        "borrar",
        borrar_fecha
    )
)

telegram_app.add_handler(

    CallbackQueryHandler(
        botones_callback
    )
)

telegram_app.add_handler(

    MessageHandler(
        filters.PHOTO,
        recibir_imagen
    )
)

telegram_app.add_handler(

    MessageHandler(

        filters.TEXT
        & ~filters.COMMAND,

        recibir_texto

    )
)

# ==========================================
# FLASK THREAD
# ==========================================
def run_flask():

    print("🔥 FLASK ACTIVO")

    flask_app.run(

        host="0.0.0.0",

        port=PORT
    )

# ==========================================
# MAIN
# ==========================================
if __name__ == "__main__":

    flask_thread = threading.Thread(
        target=run_flask
    )

    flask_thread.start()

    print("🔥 TELEGRAM ACTIVO")

    telegram_app.run_polling()