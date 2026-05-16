const CACHE = "ia-viajes-v1";

// Al instalar: no cacheamos nada crítico
// porque el overlay siempre necesita datos frescos del servidor
self.addEventListener("install", (e) => {
  self.skipWaiting();
});

self.addEventListener("activate", (e) => {
  self.clients.claim();
});

// Estrategia: network-first
// Si hay red → datos frescos del servidor
// Si no hay red → respuesta cacheada (fallback)
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
