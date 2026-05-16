# ==========================================
# IMPORTS
# ==========================================
import sys
sys.stdout.reconfigure(line_buffering=True)
import threading
import traceback
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
    recibir_texto
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

    CallbackQueryHandler(
        botones_callback
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
# TRACEBACK
# ==========================================

async def error_handler(update, context):

    print("🔥 ERROR GLOBAL 🔥")

    traceback.print_exception(
        None,
        context.error,
        context.error.__traceback__
    )

telegram_app.add_error_handler(
    error_handler
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
        target=run_flask,
        daemon=True
    )

    flask_thread.start()

    print("🔥 TELEGRAM ACTIVO")

    telegram_app.run_polling()