const CACHE = "ia-viajes-v2";

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
      url: data.url || "/operativo"
    }
  };

  e.waitUntil(
    self.registration.showNotification(
      data.title || "🚘 Nuevo viaje",
      options
    )
  );
});

// ==========================================
// NOTIFICATION CLICK — abre /operativo
// ==========================================
self.addEventListener("notificationclick", (e) => {
  e.notification.close();

  e.waitUntil(
    self.clients.matchAll({ type: "window" }).then((clients) => {
      for (const client of clients) {
        if (client.url.includes("/operativo") && "focus" in client) {
          return client.focus();
        }
      }
      return self.clients.openWindow("/operativo");
    })
  );
});