// ==========================================
// HISTORIAL.JS
// Lógica exclusiva de /historial
// Depende de fmt(), fetchJSON(), DIAS, MESES,
// iconoEstado() y labelEstado() de core.js
// ==========================================

function formatFecha(fechaStr) {
  const f = new Date(fechaStr.replace(" ", "T") + "-05:00");
  const hoy = new Date();
  const ayer = new Date();
  ayer.setDate(ayer.getDate() - 1);
  if (f.toDateString() === hoy.toDateString()) return "Hoy";
  if (f.toDateString() === ayer.toDateString()) return "Ayer";
  return `${DIAS[f.getDay()]} ${f.getDate()} ${MESES[f.getMonth()]}`;
}

function formatHora(fechaStr) {
  const f = new Date(fechaStr.replace(" ", "T") + "-05:00");
  return f.toLocaleTimeString("es-CO", { hour: "2-digit", minute: "2-digit" });
}

function labelEstadoFull(estado) {
  const map = {
    completado: "Completado", rechazado: "Rechazado",
    cancelado_usuario: "Cancelado por usuario", cancelado_conductor: "Cancelado por conductor", nuevo: "Sin acción",
  };
  return map[estado] || estado;
}

function scoreInfo(s) {
  if (s >= 9) return { label: "🔥 Excelente viaje", color: "#00ff73" };
  if (s >= 7) return { label: "✅ Buen viaje", color: "#00ff73" };
  if (s >= 5) return { label: "⚠️ Regular", color: "#ffb400" };
  return { label: "❌ Poco rentable", color: "#ff4444" };
}

function estadoColor(estado) {
  const map = {
    completado: { bg: "rgba(0,255,115,0.12)", color: "#00ff73", border: "rgba(0,255,115,0.25)" },
    rechazado: { bg: "rgba(150,150,150,0.1)", color: "rgba(255,255,255,0.4)", border: "rgba(150,150,150,0.2)" },
    cancelado_usuario: { bg: "rgba(255,140,0,0.08)", color: "#ff8c00", border: "rgba(255,140,0,0.25)" },
    cancelado_conductor: { bg: "rgba(255,60,60,0.12)", color: "#ff4444", border: "rgba(255,60,60,0.25)" },
    nuevo: { bg: "rgba(150,150,150,0.1)", color: "rgba(255,255,255,0.4)", border: "rgba(150,150,150,0.2)" },
  };
  return map[estado] || map.rechazado;
}

function filtrarViajes(viajes, tab) {
  const ahora = new Date();
  return viajes.filter(v => {
    const f = new Date(v.fecha.replace(" ", "T") + "-05:00");
    if (tab === "hoy") return f.toDateString() === ahora.toDateString();
    if (tab === "semana") { const s = new Date(); s.setDate(ahora.getDate() - 7); return f >= s; }
    if (tab === "mes") return f.getMonth() === ahora.getMonth() && f.getFullYear() === ahora.getFullYear();
    return true;
  });
}

let todosLosViajes = [];
let tabActual = "todos";

// ==========================================
// SHEET DE DETALLE
// ==========================================
function abrirDetalle(v) {
  const esCompletado = v.estado === "completado";
  const dinero_por_min = v.tiempo_total > 0 ? v.dinero / v.tiempo_total : 0;
  const dinero_por_km = v.distancia_total > 0 ? v.dinero / v.distancia_total : 0;
  const dinero_por_hora = dinero_por_min * 60;
  const sc = scoreInfo(v.score_visual);
  const ec = estadoColor(v.estado);
  const moneyClass = esCompletado ? "green" : "dim";

  document.getElementById("sheet-inner").innerHTML = `
    <div class="sheet-header">
      <span class="sheet-tipo">${v.tipo_viaje || "Uber"}</span>
      <button class="btn-close" onclick="cerrarDetalle()"><i class="ti ti-x"></i></button>
    </div>
    <p class="sheet-money ${moneyClass}">$${fmt(v.dinero)}</p>
    <div class="sheet-estado" style="background:${ec.bg}; color:${ec.color}; border:1px solid ${ec.border};">
      ${labelEstadoFull(v.estado)}
    </div>

    <div class="divider"></div>

    <div class="detail-grid">
      <div class="detail-card">
        <p class="detail-label">Por hora</p>
        <p class="detail-val">${esCompletado ? `$${fmt(dinero_por_hora)}` : "—"}<span>/hr</span></p>
      </div>
      <div class="detail-card">
        <p class="detail-label">Por minuto</p>
        <p class="detail-val">${esCompletado ? `$${fmt(dinero_por_min)}` : "—"}<span>/min</span></p>
      </div>
      <div class="detail-card">
        <p class="detail-label">Por km</p>
        <p class="detail-val">${esCompletado ? `$${fmt(dinero_por_km)}` : "—"}<span>/km</span></p>
      </div>
      <div class="detail-card">
        <p class="detail-label">Distancia total</p>
        <p class="detail-val">${v.distancia_total}<span>km</span></p>
      </div>
      <div class="detail-card">
        <p class="detail-label">Tiempo total</p>
        <p class="detail-val">${v.tiempo_total}<span>min</span></p>
      </div>
      <div class="detail-card">
        <p class="detail-label">Fecha</p>
        <p class="detail-val" style="font-size:13px;">${formatHora(v.fecha)}</p>
      </div>
    </div>

    ${esCompletado ? `
    <div class="score-bar-wrap">
      <div class="score-bar-header">
        <span class="score-bar-label">Score del viaje</span>
        <span class="score-bar-val">${v.score_visual}<span style="font-size:13px; color:var(--text-dim); font-weight:500;">/10</span></span>
      </div>
      <div class="score-bar-bg">
        <div class="score-bar-fill" style="width:${v.score_visual * 10}%; background:${sc.color};"></div>
      </div>
      <p class="score-estado" style="color:${sc.color};">${sc.label}</p>
    </div>` : ""}
  `;

  document.getElementById("overlay").classList.add("visible");
}

function cerrarDetalle(e) {
  if (e && e.target !== document.getElementById("overlay")) return;
  document.getElementById("overlay").classList.remove("visible");
}

// ==========================================
// RENDER LISTA
// ==========================================
function renderViajes(viajes) {
  const content = document.getElementById("content");
  document.getElementById("header-sub").textContent = `${viajes.length} viaje${viajes.length !== 1 ? "s" : ""}`;

  if (viajes.length === 0) {
    content.innerHTML = `<div class="empty-state"><div class="empty-icon">🚖</div><p class="empty-text">Sin viajes en este período</p></div>`;
    return;
  }

  const grupos = {};
  viajes.forEach(v => {
    const key = formatFecha(v.fecha);
    if (!grupos[key]) grupos[key] = [];
    grupos[key].push(v);
  });

  let html = "";
  for (const [fecha, lista] of Object.entries(grupos)) {
    html += `<p class="fecha-label">${fecha}</p>`;
    lista.forEach(v => {
      const { cls, icon } = iconoEstado(v.estado);
      const esCompletado = v.estado === "completado";
      const meta = esCompletado
        ? `${v.distancia_total}km · ${v.tiempo_total}min · $${fmt(v.dinero / v.distancia_total)}/km`
        : `${v.distancia_total}km · ${v.tiempo_total}min`;

      // data-id en vez de JSON embebido en el onclick: más robusto ante
      // caracteres especiales en cualquier campo del viaje
      html += `
      <div class="viaje-item" data-id="${v.id}">
        <div class="viaje-left">
          <div class="viaje-icon ${cls}"><i class="ti ${icon}"></i></div>
          <div class="viaje-info">
            <p class="viaje-dinero ${esCompletado ? '' : 'dim'}">$${fmt(v.dinero)}</p>
            <p class="viaje-meta">${meta}</p>
          </div>
        </div>
        <div class="viaje-right">
          <div class="estado-badge badge-${v.estado}">${labelEstado(v.estado)}</div>
          <p class="viaje-hora">${formatHora(v.fecha)}</p>
        </div>
      </div>`;
    });
  }
  content.innerHTML = html;

  // Delegar clicks: buscamos el viaje por id en el array ya cargado
  content.querySelectorAll(".viaje-item").forEach(item => {
    item.addEventListener("click", () => {
      const id = parseInt(item.dataset.id, 10);
      const viaje = todosLosViajes.find(v => v.id === id);
      if (viaje) abrirDetalle(viaje);
    });
  });
}

// ==========================================
// CARGA Y TABS
// ==========================================
async function cargarHistorial() {
  const resp = await fetchJSON("/api/historial");
  if (!resp.ok) return;

  todosLosViajes = resp.data;
  renderViajes(filtrarViajes(todosLosViajes, tabActual));
}

function cambiarTab(tab, btn) {
  document.querySelectorAll(".tab").forEach(t => t.classList.remove("active"));
  btn.classList.add("active");
  tabActual = tab;
  renderViajes(filtrarViajes(todosLosViajes, tab));
}

cargarHistorial();
document.addEventListener("visibilitychange", () => {
  if (document.visibilityState === "visible") cargarHistorial();
});
