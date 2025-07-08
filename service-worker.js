const CACHE_NAME = 'midni-cache-v1';
const urlsToCache = [
  '/index.html',
  '/midni.html',
  '/dni.html',
  '/styles.css',
  '/manifest.json',
  '/icons/logo192.png',
  '/icons/logo512.png'
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => {
      return cache.addAll(urlsToCache);
    })
  );
  console.log('Service Worker instalado');
});

self.addEventListener('activate', event => {
  // Limpiar cachés antiguas si existieran
  event.waitUntil(
    caches.keys().then(cacheNames =>
      Promise.all(
        cacheNames.map(cache => {
          if (cache !== CACHE_NAME) {
            return caches.delete(cache);
          }
        })
      )
    )
  );
  console.log('Service Worker activado y cachés antiguas eliminadas');
});

self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request).then(response => {
      // Devuelve la respuesta en caché si existe o realiza la petición a la red
      return response || fetch(event.request).catch(() => {
        // Opcional: fallback si no hay conexión y no está cacheado
        if (event.request.mode === 'navigate') {
          return caches.match('/index.html');
        }
      });
    })
  );
});
