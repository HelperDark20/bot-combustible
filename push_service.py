# ==========================================
# PUSH SERVICE
# ==========================================
import json
import base64
from pywebpush import webpush, WebPushException

from config import (
    VAPID_PRIVATE_KEY,
    VAPID_PUBLIC_KEY,
    VAPID_EMAIL
)

# ==========================================
# SUBSCRIPTIONS EN MEMORIA
# ==========================================
subscriptions = []

# ==========================================
# AGREGAR SUBSCRIPTION
# ==========================================
def agregar_subscription(sub):

    # Evitar duplicados por endpoint
    for s in subscriptions:
        if s.get("endpoint") == sub.get("endpoint"):
            return

    subscriptions.append(sub)

    print(f"📲 SUBSCRIPTION AGREGADA: {len(subscriptions)} total")

# ==========================================
# ENVIAR PUSH
# ==========================================
def enviar_push(data: dict):

    if not subscriptions:
        print("⚠️ No hay subscriptions registradas")
        return

    private_key_raw = base64.urlsafe_b64decode(
        VAPID_PRIVATE_KEY + "=="
    )

    for sub in subscriptions[:]:

        try:

            webpush(
                subscription_info=sub,
                data=json.dumps(data),
                vapid_private_key=VAPID_PRIVATE_KEY,
                vapid_claims={
                    "sub": VAPID_EMAIL
                }
            )

            print("✅ PUSH ENVIADO")

        except WebPushException as e:

            print(f"🔥 PUSH ERROR: {e}")

            # Si el endpoint ya no existe, remover
            if e.response and e.response.status_code in [404, 410]:
                subscriptions.remove(sub)
                print("🗑 Subscription removida")
