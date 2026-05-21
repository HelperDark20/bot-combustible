import threading

usuarios_configurando = {}

usuarios_borrando_fecha = set()

message_id_auxiliar = None

# ==========================================
# PANEL OPERATIVO
# ==========================================

viaje_nuevo = None        # llega notificación, espera Aceptar/Rechazar

viaje_en_curso = None     # fue aceptado, en progreso

viaje_pendiente = None    # hay uno en curso y llegó otro aceptado

vista_actual = "curso"

message_id_operativo = None

STATE_LOCK = threading.RLock()