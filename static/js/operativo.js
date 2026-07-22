// ==========================================
// OPERATIVO.JS
// Lógica exclusiva de /operativo
// Depende de fmt() definido en core.js
// ==========================================

function scoreClass(s) {
  if (s >= 8) return "score-high";
  if (s >= 5) return "score-mid";
  return "score-low";
}

let pollingActivo = true;

function toggleCancelar(id) {
  const el = document.getElementById(id);
  el.classList.toggle("visible");
  // Pausar polling si hay menú abierto
  pollingActivo = !el.classList.contains("visible");
}

// ==========================================
// RENDER
// ==========================================
function renderContent(data) {
  const { viaje_nuevo, viaje_en_curso, viaje_pendiente } = data;
  const content = document.getElementById("content");

  if (!viaje_nuevo && !viaje_en_curso && !viaje_pendiente) {
    content.innerHTML = `
      <div class="empty-state">
        <div class="empty-icon">🚖</div>
        <p class="empty-text">Sin viajes activos</p>
      </div>`;
    return;
  }

  let html = "";

  // ======================================
  // VIAJE NUEVO
  // ======================================
  if (viaje_nuevo) {
    const v = viaje_nuevo;
    const sc = scoreClass(v.score_visual);
    html += `
    <div class="card card-nuevo">
      <div class="card-label label-nuevo">
        <i class="ti ti-bell-ringing"></i> Nuevo viaje
      </div>
      <div class="card-money">$${fmt(v.ganancia)}</div>
      <div class="card-meta">
        <span>📍 ${v.distancia_total}km</span>
        <span>⏱ ${v.tiempo_total}min</span>
        <span>💵 ${fmt(v.dinero_por_km)}/km</span>
        <span>💰 ${fmt(v.dinero_por_hora)}/hr</span>
        <span>💸 ${fmt(v.dinero_por_min)}/min</span>
      </div>
      <div style="display:flex; align-items:center; gap:8px; margin-bottom:14px; flex-wrap:wrap;">
        <div class="score-badge ${sc}">⭐ ${v.score_visual}/10 · ${v.estado_score}</div>
        ${v.tipo_viaje ? `<div style="background:rgba(255,255,255,0.06); border:1px solid rgba(255,255,255,0.12); border-radius:8px; padding:3px 10px; font-size:12px; font-weight:700; color:rgba(255,255,255,0.6);">${v.tipo_viaje}</div>` : ""}
      </div>
      <div class="btn-row btn-row-2">
        <a href="/web/aceptar" class="btn btn-green">
          <i class="ti ti-check" style="font-size:16px;"></i> Aceptar
        </a>
        <a href="/web/rechazar" class="btn btn-red">
          <i class="ti ti-x" style="font-size:16px;"></i> Rechazar
        </a>
      </div>
    </div>`;
  }

  // ======================================
  // VIAJE EN CURSO
  // ======================================
  if (viaje_en_curso) {
    const v = viaje_en_curso;
    const sc = scoreClass(v.score_visual);
    html += `
    <div class="card card-curso">
      <div class="card-label label-curso">
        <i class="ti ti-car"></i> Viaje en curso
      </div>
      <div class="card-money">$${fmt(v.ganancia)}</div>
      <div class="card-meta">
        <span>📍 ${v.distancia_total}km</span>
        <span>⏱ ${v.tiempo_total}min</span>
        <span>💵 ${fmt(v.dinero_por_km)}/km</span>
      </div>
      <div class="score-badge ${sc}">⭐ ${v.score_visual}/10</div>
      <div class="btn-row btn-row-2">
        <a href="/web/finalizar" class="btn btn-green">
          <i class="ti ti-check" style="font-size:16px;"></i> Finalizar
        </a>
        <button class="btn btn-red" onclick="toggleCancelar('cancelar-curso')">
          <i class="ti ti-x" style="font-size:16px;"></i> Cancelar
        </button>
      </div>
      <div class="cancelar-opts" id="cancelar-curso">
        <p class="cancelar-label">¿Quién canceló?</p>
        <div class="btn-row btn-row-2">
          <a href="/web/cancelar/usuario?tipo=curso" class="btn btn-gray" style="font-size:12px; height:42px;">
            <i class="ti ti-user" style="font-size:14px;"></i> Usuario
          </a>
          <a href="/web/cancelar/conductor?tipo=curso" class="btn btn-gray" style="font-size:12px; height:42px;">
            <i class="ti ti-steering-wheel" style="font-size:14px;"></i> Conductor
          </a>
        </div>
      </div>
    </div>`;
  }

  // ======================================
  // VIAJE PENDIENTE
  // ======================================
  if (viaje_pendiente) {
    const v = viaje_pendiente;
    const sc = scoreClass(v.score_visual);
    html += `
    <div class="card card-pendiente">
      <div class="card-label label-pendiente">
        <i class="ti ti-clock"></i> Viaje pendiente
      </div>
      <div class="card-money">$${fmt(v.ganancia)}</div>
      <div class="card-meta">
        <span>📍 ${v.distancia_total}km</span>
        <span>⏱ ${v.tiempo_total}min</span>
        <span>💵 ${fmt(v.dinero_por_km)}/km</span>
      </div>
      <div class="score-badge ${sc}">⭐ ${v.score_visual}/10</div>
      <div class="btn-row btn-row-1">
        <button class="btn btn-red" onclick="toggleCancelar('cancelar-pendiente')">
          <i class="ti ti-x" style="font-size:16px;"></i> Cancelar
        </button>
      </div>
      <div class="cancelar-opts" id="cancelar-pendiente">
        <p class="cancelar-label">¿Quién canceló?</p>
        <div class="btn-row btn-row-2">
          <a href="/web/cancelar/usuario?tipo=pendiente" class="btn btn-gray" style="font-size:12px; height:42px;">
            <i class="ti ti-user" style="font-size:14px;"></i> Usuario
          </a>
          <a href="/web/cancelar/conductor?tipo=pendiente" class="btn btn-gray" style="font-size:12px; height:42px;">
            <i class="ti ti-steering-wheel" style="font-size:14px;"></i> Conductor
          </a>
        </div>
      </div>
    </div>`;
  }

  content.innerHTML = html;
}

// ==========================================
// POLLING cada 2 segundos
// ==========================================
async function polling() {
  if (!pollingActivo) return;

  const data = await fetchJSON("/api/operativo");
  if (!data.ok) return;

  renderContent(data);
}

let intervaloPolling = setInterval(polling, 2000);

// Cargar al abrir
polling();

// Recargar cuando la app vuelve a primer plano
document.addEventListener("visibilitychange", () => {
  if (document.visibilityState === "visible") {
    polling();
  }
});
