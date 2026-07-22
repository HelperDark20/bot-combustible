// ==========================================
// INICIO.JS
// Lógica exclusiva de /inicio
// Depende de fmt(), fetchJSON(), DIAS, MESES,
// iconoEstado() y labelEstado() de core.js
// ==========================================

// ==========================================
// FECHA HOY
// ==========================================
function mostrarFechaHoy() {
  const hoy = new Date();
  document.getElementById("fecha-hoy").textContent =
    `${DIAS[hoy.getDay()]} ${hoy.getDate()} ${MESES[hoy.getMonth()]}`;
}

// ==========================================
// HELPERS
// ==========================================
function tiempoRelativo(fechaStr) {
  const fecha = new Date(fechaStr.replace(" ", "T") + "-05:00");
  const diff = Math.floor((Date.now() - fecha.getTime()) / 60000);
  if (diff < 1) return "ahora";
  if (diff < 60) return `hace ${diff}min`;
  if (diff < 1440) return `hace ${Math.floor(diff / 60)}hr`;
  return `hace ${Math.floor(diff / 1440)}d`;
}

// ==========================================
// CARGAR DATOS
// ==========================================
async function cargarInicio() {
  const resp = await fetchJSON("/api/inicio");
  if (!resp.ok) return;

  const { stats, ultimos_viajes } = resp.data;

  // Stats
  document.getElementById("ganancia-monto").textContent = `$${fmt(stats.ganancia)}`;
  document.getElementById("stat-viajes").textContent = stats.viajes;
  document.getElementById("stat-score").textContent = stats.score_prom || "—";
  document.getElementById("stat-km").textContent = stats.km_total ? `${stats.km_total}km` : "—";
  document.getElementById("total-badge").textContent = `${stats.total_db} viajes`;

  // Últimos viajes
  const lista = document.getElementById("viajes-list");

  if (ultimos_viajes.length === 0) {
    lista.innerHTML = `
      <div style="text-align:center; padding:30px; color:var(--text-dim); font-size:14px;">
        Sin viajes hoy
      </div>`;
    return;
  }

  lista.innerHTML = ultimos_viajes.map(v => {
    const { cls, icon } = iconoEstado(v.estado);
    const esCompletado = v.estado === "completado";
    return `
    <div class="viaje-item">
      <div class="viaje-left">
        <div class="viaje-icon ${cls}">
          <i class="ti ${icon}"></i>
        </div>
        <div class="viaje-info">
          <p class="viaje-dinero ${esCompletado ? '' : 'dim'}">$${fmt(v.dinero)}</p>
          <p class="viaje-meta">${v.distancia_total}km · ${v.tiempo_total}min${esCompletado ? ` · $${fmt(v.dinero / v.distancia_total)}/km` : ''}</p>
        </div>
      </div>
      <div class="viaje-right">
        <div class="estado-badge badge-${v.estado}">${labelEstado(v.estado)}</div>
        <p class="viaje-hora">${tiempoRelativo(v.fecha)}</p>
      </div>
    </div>`;
  }).join("");
}

mostrarFechaHoy();
cargarInicio();

// Recargar al volver a la app
document.addEventListener("visibilitychange", () => {
  if (document.visibilityState === "visible") cargarInicio();
});