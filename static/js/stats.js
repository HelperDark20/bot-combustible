// ==========================================
// STATS.JS
// Lógica exclusiva de /stats
// Depende de fmt() y fetchJSON() definidos en core.js
// ==========================================

function scoreColor(s) {
  if (s >= 8) return "green";
  if (s >= 5) return "";
  return "red";
}

function scoreLabel(s) {
  if (s >= 8) return "Buen rendimiento";
  if (s >= 5) return "Rendimiento regular";
  return "Rendimiento bajo";
}

function skeletonStats() {
  return `
    <div style="height:120px;" class="skeleton"></div>
    <div class="grid-2">
      <div style="height:90px;" class="skeleton"></div>
      <div style="height:90px;" class="skeleton"></div>
    </div>
    <div class="grid-2">
      <div style="height:90px;" class="skeleton"></div>
      <div style="height:90px;" class="skeleton"></div>
    </div>
    <div style="height:160px;" class="skeleton"></div>`;
}

let tabActual = "hoy";

async function cargarStats(periodo) {
  const content = document.getElementById("content");
  content.innerHTML = skeletonStats();

  // Se piden en paralelo: los stats del período y el costo real de combustible
  const [statsResp, configResp] = await Promise.all([
    fetchJSON(`/api/stats/${periodo}`),
    fetchJSON("/api/config")
  ]);

  if (!statsResp.ok) return;

  const d = statsResp.data;

  // Si /api/config falla por algún motivo, no rompemos la vista —
  // simplemente no descontamos combustible (mejor que mostrar un dato falso)
  const costoKm = configResp.ok ? configResp.data.costo_km : 0;

  const gastoCombustible = d.km_total * costoKm;
  const neta = d.ganancia - gastoCombustible;
  const sc = d.score_prom || 0;

  content.innerHTML = `
    <div class="card-ganancia">
      <p class="ganancia-label">Ganancia bruta</p>
      <p class="ganancia-monto">$${fmt(d.ganancia)}</p>
      <p class="ganancia-sub">${d.completados} viaje${d.completados !== 1 ? "s" : ""} completado${d.completados !== 1 ? "s" : ""}</p>
    </div>

    <div class="grid-2">
      <div class="card">
        <p class="card-label">Ganancia neta</p>
        <p class="card-val">$${fmt(neta)}</p>
        <p class="card-hint">${configResp.ok ? "desc. combustible" : "sin datos de combustible"}</p>
      </div>
      <div class="card">
        <p class="card-label">Score promedio</p>
        <p class="card-val">${sc}<span>/10</span></p>
        <p class="card-hint ${scoreColor(sc)}">${scoreLabel(sc)}</p>
      </div>
    </div>

    <div class="grid-2">
      <div class="card">
        <p class="card-label">KM recorridos</p>
        <p class="card-val">${d.km_total}<span>km</span></p>
        <p class="card-hint">completados</p>
      </div>
      <div class="card">
        <p class="card-label">Gasto combustible</p>
        <p class="card-val">$${fmt(gastoCombustible)}</p>
        <p class="card-hint red">${configResp.ok ? `$${fmt(costoKm)}/km` : "configura tu combustible"}</p>
      </div>
    </div>

    <div class="desglose">
      <p class="desglose-title">Desglose de viajes</p>
      <div class="desglose-row">
        <div class="desglose-left">
          <div class="dot" style="background:#00ff73;"></div>
          <span class="desglose-label">Completados</span>
        </div>
        <span class="desglose-val">${d.completados}</span>
      </div>
      <div class="desglose-row">
        <div class="desglose-left">
          <div class="dot" style="background:#ff4444;"></div>
          <span class="desglose-label">Cancelados</span>
        </div>
        <span class="desglose-val">${d.cancelados}</span>
      </div>
      <div class="desglose-row">
        <div class="desglose-left">
          <div class="dot" style="background:rgba(150,150,150,0.5);"></div>
          <span class="desglose-label">Rechazados</span>
        </div>
        <span class="desglose-val">${d.rechazados || 0}</span>
      </div>
      <div class="desglose-row">
        <div class="desglose-left">
          <div class="dot" style="background:rgba(255,255,255,0.2);"></div>
          <span class="desglose-label">Total</span>
        </div>
        <span class="desglose-val">${d.total}</span>
      </div>
    </div>`;
}

function cambiarTab(periodo, btn) {
  document.querySelectorAll(".tab").forEach(t => t.classList.remove("active"));
  btn.classList.add("active");
  tabActual = periodo;
  cargarStats(periodo);
}

cargarStats("hoy");

document.addEventListener("visibilitychange", () => {
  if (document.visibilityState === "visible") cargarStats(tabActual);
});