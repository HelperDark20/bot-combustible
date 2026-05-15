import threading

usuarios_configurando = {}

usuarios_borrando_fecha = set()

message_id_auxiliar = None

# ==========================================
# PANEL OPERATIVO
# ==========================================

viaje_en_curso = None

viaje_pendiente = None

vista_actual = "curso"

message_id_operativo = None

STATE_LOCK = threading.RLock()