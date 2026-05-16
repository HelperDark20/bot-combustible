const CACHE = "ia-viajes-v1";

self.addEventListener("install", (e) => {
  self.skipWaiting();
});

self.addEventListener("activate", (e) => {
  self.clients.claim();
});

// ==========================================
// FETCH — network first
// ==========================================
self.addEventListener("fetch", (e) => {
  e.respondWith(
    fetch(e.request)
      .then((response) => {
        const clone = response.clone();
        caches.open(CACHE).then((cache) => {
          cache.put(e.request, clone);
        });
        return response;
      })
      .catch(() => {
        return caches.match(e.request);
      })
  );
});

// ==========================================
// PUSH — recibir notificación
// ==========================================
self.addEventListener("push", (e) => {

  let data = {};

  try {
    data = e.data.json();
  } catch (err) {
    data = { title: "IA Viajes", body: "Nuevo viaje disponible" };
  }

  const options = {
    body: data.body || "Nuevo viaje disponible",
    icon: "/static/icon-192.png",
    badge: "/static/icon-192.png",
    vibrate: [200, 100, 200],
    tag: "nuevo-viaje",
    renotify: true,
    data: {
      url: data.url || "/overlay"
    },
    actions: [
      {
        action: "aceptar",
        title: "✅ Aceptar"
      },
      {
        action: "rechazar",
        title: "❌ Rechazar"
      }
    ]
  };

  e.waitUntil(
    self.registration.showNotification(
      data.title || "🚘 Nuevo viaje",
      options
    )
  );

});

// ==========================================
// NOTIFICATION CLICK
// ==========================================
self.addEventListener("notificationclick", (e) => {

  e.notification.close();

  // ======================================
  // ACEPTAR
  // ======================================
  if (e.action === "aceptar") {

    e.waitUntil(
      fetch("/web/finalizar").then(() => {
        return self.clients.openWindow("/overlay");
      })
    );

  // ======================================
  // RECHAZAR
  // ======================================
  } else if (e.action === "rechazar") {

    e.waitUntil(
      fetch("/web/cancelar").then(() => {
        return self.clients.openWindow("/overlay");
      })
    );

  // ======================================
  // TAP NOTIFICACIÓN
  // ======================================
  } else {

    e.waitUntil(
      self.clients.matchAll({ type: "window" }).then((clients) => {
        for (const client of clients) {
          if (client.url.includes("/overlay") && "focus" in client) {
            return client.focus();
          }
        }
        return self.clients.openWindow("/overlay");
      })
    );

  }

});