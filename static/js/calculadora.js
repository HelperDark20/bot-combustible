// ==========================================
// CALCULADORA.JS
// Lógica exclusiva de /calculadora
// Depende de fmt() y fetchJSON() definidos en core.js
// ==========================================

// ==========================================
// CARD 1 — TANQUEADA
// ==========================================
async function calcularTanqueada() {
  const monto = parseFloat(document.getElementById("t-monto").value);
  const km_l = parseFloat(document.getElementById("t-kml").value);
  const valor_galon = parseFloat(document.getElementById("t-galon").value);
  const err = document.getElementById("error-tanqueada");
  const resultado = document.getElementById("resultado-tanqueada");

  if (!monto || monto <= 0 || !km_l || km_l <= 0 || !valor_galon || valor_galon <= 0) {
    err.classList.add("visible");
    resultado.classList.remove("visible");
    return;
  }
  err.classList.remove("visible");

  const resp = await fetchJSON("/api/calculadora/tanqueada", {
    method: "POST",
    body: { monto, km_l, valor_galon }
  });

  if (!resp.ok) {
    err.textContent = resp.error;
    err.classList.add("visible");
    return;
  }

  document.getElementById("km-posibles").textContent = `${resp.data.km_posibles} km`;
  document.getElementById("costo-km-tanqueada").textContent = `$${fmt(resp.data.costo_km)}`;
  resultado.classList.add("visible");
}

// ==========================================
// CARD 2 — EVALUAR VIAJE
// ==========================================
async function calcularEvaluar() {
  const ganancia = parseFloat(document.getElementById("e-ganancia").value);
  const distancia_total = parseFloat(document.getElementById("e-distancia").value);
  const tiempo_total = parseFloat(document.getElementById("e-tiempo").value) || 0;
  const km_l = parseFloat(document.getElementById("e-kml").value);
  const valor_galon = parseFloat(document.getElementById("e-galon").value);
  const err = document.getElementById("error-evaluar");
  const resultado = document.getElementById("resultado-evaluar");

  if (!ganancia || ganancia <= 0 || !distancia_total || distancia_total <= 0 || !km_l || km_l <= 0 || !valor_galon || valor_galon <= 0) {
    err.classList.add("visible");
    resultado.classList.remove("visible");
    return;
  }
  err.classList.remove("visible");

  const resp = await fetchJSON("/api/calculadora/evaluar", {
    method: "POST",
    body: { ganancia, distancia_total, tiempo_total, km_l, valor_galon }
  });

  if (!resp.ok) {
    err.textContent = resp.error;
    err.classList.add("visible");
    return;
  }

  const d = resp.data;

  document.getElementById("eval-neta").textContent = `$${fmt(d.ganancia_neta)} neto`;
  document.getElementById("eval-dinero-km").textContent = `$${fmt(d.dinero_por_km)}`;
  document.getElementById("eval-dinero-hora").textContent = tiempo_total > 0 ? `$${fmt(d.dinero_por_hora)}` : "—";
  document.getElementById("eval-gasto").textContent = `$${fmt(d.gasto_combustible)}`;
  document.getElementById("eval-score").textContent = `${d.score_visual}/10`;

  const v = document.getElementById("eval-veredicto");
  v.textContent = d.estado_score;
  v.className = "veredicto " + (d.score_visual >= 7 ? "v-good" : d.score_visual >= 5 ? "v-mid" : "v-bad");

  resultado.classList.add("visible");
}

// ==========================================
// CARD 3 — META DEL DÍA
// ==========================================
async function calcularMeta() {
  const meta = parseFloat(document.getElementById("m-meta").value);
  const km_l = parseFloat(document.getElementById("m-kml").value);
  const valor_galon = parseFloat(document.getElementById("m-galon").value);
  const err = document.getElementById("error-meta");
  const resultado = document.getElementById("resultado-meta");

  if (!meta || meta <= 0 || !km_l || km_l <= 0 || !valor_galon || valor_galon <= 0) {
    err.classList.add("visible");
    resultado.classList.remove("visible");
    return;
  }
  err.classList.remove("visible");

  const resp = await fetchJSON("/api/calculadora/meta", {
    method: "POST",
    body: { meta, km_l, valor_galon }
  });

  if (!resp.ok) {
    err.textContent = resp.error;
    err.classList.add("visible");
    return;
  }

  const d = resp.data;

  document.getElementById("meta-neta-hoy").textContent = `$${fmt(d.neta_hoy)}`;
  document.getElementById("meta-promedio").textContent = d.completados > 0 ? `$${fmt(d.promedio_neto)}` : "—";

  const badge = document.getElementById("meta-viajes-faltan");

  if (d.restante <= 0) {
    document.getElementById("meta-restante").textContent = `¡Meta cumplida! 🎉`;
    badge.textContent = `Ya superaste tu meta de hoy`;
    badge.className = "veredicto v-good";
  } else {
    document.getElementById("meta-restante").textContent = `$${fmt(d.restante)} restantes`;
    if (d.promedio_neto > 0) {
      const viajesFaltan = Math.ceil(d.restante / d.promedio_neto);
      badge.textContent = `≈ ${viajesFaltan} viaje${viajesFaltan !== 1 ? "s" : ""} más, al ritmo de hoy`;
      badge.className = "veredicto v-mid";
    } else {
      badge.textContent = `Aún no tienes viajes completados hoy para estimar`;
      badge.className = "veredicto v-mid";
    }
  }

  resultado.classList.add("visible");
}