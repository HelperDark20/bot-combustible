# ==========================================
# PUSH SERVICE
# ==========================================
import json
import sqlite3
from pywebpush import webpush, WebPushException

from config import (
    VAPID_PRIVATE_KEY,
    VAPID_PUBLIC_KEY,
    VAPID_EMAIL
)

# ==========================================
# CREAR TABLA SUBSCRIPTIONS
# ==========================================
def crear_tabla_subscriptions():
    conn = sqlite3.connect("viajes.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS push_subscriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            endpoint TEXT UNIQUE,
            data TEXT
        )
    """)
    conn.commit()
    conn.close()

crear_tabla_subscriptions()

# ==========================================
# AGREGAR SUBSCRIPTION
# ==========================================
def agregar_subscription(sub):
    try:
        conn = sqlite3.connect("viajes.db")
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO push_subscriptions (endpoint, data)
            VALUES (?, ?)
        """, (sub.get("endpoint"), json.dumps(sub)))
        conn.commit()
        conn.close()
        print(f"📲 SUBSCRIPTION GUARDADA EN DB")
    except Exception as e:
        print(f"🔥 ERROR GUARDANDO SUBSCRIPTION: {e}")

# ==========================================
# ENVIAR PUSH
# ==========================================
def enviar_push(data: dict):
    try:
        conn = sqlite3.connect("viajes.db")
        cursor = conn.cursor()
        cursor.execute("SELECT endpoint, data FROM push_subscriptions")
        rows = cursor.fetchall()
        conn.close()
    except Exception as e:
        print(f"🔥 ERROR LEYENDO SUBSCRIPTIONS: {e}")
        return

    if not rows:
        print("⚠️ No hay subscriptions registradas")
        return

    for endpoint, sub_data in rows:
        try:
            sub = json.loads(sub_data)

            webpush(
                subscription_info=sub,
                data=json.dumps(data),
                vapid_private_key=VAPID_PRIVATE_KEY,
                vapid_claims={
                    "sub": VAPID_EMAIL
                },
                content_encoding="aes128gcm"
            )

            print("✅ PUSH ENVIADO")

        except WebPushException as e:
            print(f"🔥 PUSH ERROR: {e}")

            if e.response and e.response.status_code in [404, 410]:
                conn = sqlite3.connect("viajes.db")
                cursor = conn.cursor()
                cursor.execute("DELETE FROM push_subscriptions WHERE endpoint = ?", (endpoint,))
                conn.commit()
                conn.close()
                print("🗑 Subscription removida")

        except Exception as e:
            print(f"🔥 PUSH ERROR GENERAL: {e}")