// ==========================================
// CORE.JS
// Utilidades compartidas por toda la PWA
// Se carga en TODAS las páginas via _head.html
// ==========================================

/**
 * Formatea un número con separador de miles estilo COP
 * Ej: fmt(15000) -> "15.000"
 */
function fmt(n) {
  return String(Math.round(n)).replace(/\B(?=(\d{3})+(?!\d))/g, ".");
}

/**
 * Wrapper de fetch con manejo de errores consistente.
 * Devuelve SIEMPRE { ok, error, data } — nunca hace spread del JSON
 * recibido, para que funcione igual si el endpoint responde un
 * objeto ({...}) o un array ([...], como /api/historial).
 *
 * Uso:
 *   const res = await fetchJSON("/api/algo", { method: "POST", body: {...} });
 *   if (!res.ok) { mostrarError(res.error); return; }
 *   usar(res.data);
 */
async function fetchJSON(url, options = {}) {
  const opts = { ...options };

  if (opts.body && typeof opts.body !== "string") {
    opts.body = JSON.stringify(opts.body);
    opts.headers = { "Content-Type": "application/json", ...(opts.headers || {}) };
  }

  try {
    const res = await fetch(url, opts);
    const json = await res.json();

    if (!res.ok) {
      const msg = (json && !Array.isArray(json) && json.error) || `Error ${res.status}`;
      return { ok: false, error: msg, data: null };
    }

    return { ok: true, error: null, data: json };
  } catch (e) {
    console.error(`fetchJSON error [${url}]:`, e);
    return { ok: false, error: "Error de conexión", data: null };
  }
}

/**
 * Nombres de días y meses en español, usados en inicio e historial
 */
const DIAS = ["Domingo","Lunes","Martes","Miércoles","Jueves","Viernes","Sábado"];
const MESES = ["Enero","Febrero","Marzo","Abril","Mayo","Junio","Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"];

/**
 * Mapea el estado de un viaje a su ícono/clase visual.
 * Incluye "nuevo" (viaje sin acción tomada), usado solo en historial.
 */
function iconoEstado(estado) {
  const map = {
    completado: { cls: "icon-completado", icon: "ti-check" },
    rechazado: { cls: "icon-rechazado", icon: "ti-ban" },
    cancelado_usuario: { cls: "icon-cancelado_usuario", icon: "ti-user-x" },
    cancelado_conductor: { cls: "icon-cancelado_conductor", icon: "ti-x" },
    nuevo: { cls: "icon-nuevo", icon: "ti-clock" },
  };
  return map[estado] || { cls: "icon-rechazado", icon: "ti-ban" };
}

/**
 * Etiqueta corta del estado (para badges en listas)
 */
function labelEstado(estado) {
  const map = {
    completado: "Completado",
    rechazado: "Rechazado",
    cancelado_usuario: "Canc. usuario",
    cancelado_conductor: "Canc. conductor",
    nuevo: "Sin acción",
  };
  return map[estado] || estado;
}

/**
 * Registro estándar del service worker.
 * Se llama al final de cada página.
 */
function registrarServiceWorker() {
  if ("serviceWorker" in navigator) {
    navigator.serviceWorker.register("/sw.js");
  }
}

// Auto-registro al cargar core.js
registrarServiceWorker();