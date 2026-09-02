// Service Worker Seguro para CHAMBA RD PWA
// Versión: 1.0.0
const CACHE_NAME = 'chamba-rd-cache-v1';
const PUBLIC_ASSETS = [
  '/',
  '/index.html',
  '/manifest.webmanifest',
  '/icons/icon-192.png',
  '/icons/icon-512.png',
  '/icons/icon-maskable-192.png',
  '/icons/icon-maskable-512.png'
];

// Instalación: Pre-almacenar recursos públicos estáticos
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(PUBLIC_ASSETS).catch((err) => {
        console.warn('CHAMBA RD SW: Algunos activos públicos no se pudieron precachear:', err);
      });
    })
  );
  self.skipWaiting();
});

// Activación: Limpieza de cachés obsoletas y control inmediato
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(
        keys.map((key) => {
          if (key !== CACHE_NAME) {
            return caches.delete(key);
          }
        })
      );
    }).then(() => self.clients.claim())
  );
});

// Estrategia de Fetch Seguro
// REGLA CRÍTICA DE SEGURIDAD:
// NUNCA cachear contraseñas, tokens, llamadas a API de pagos, comprobantes privados o datos sensibles.
self.addEventListener('fetch', (event) => {
  const request = event.request;
  const url = new URL(request.url);

  // 1. Las peticiones que no sean GET (POST, PUT, DELETE) siempre van a la red sin caché
  if (request.method !== 'GET') {
    return;
  }

  // 2. Las rutas de API REST (/api/v1/) NUNCA se guardan en caché para proteger datos privados
  if (url.pathname.startsWith('/api/') || url.pathname.includes('/auth/') || url.pathname.includes('/pagos/') || url.pathname.includes('/admin/')) {
    event.respondWith(
      fetch(request).catch(() => {
        return new Response(
          JSON.stringify({ 
            error: 'Sin conexión a internet. Esta acción requiere conexión al servidor seguro de CHAMBA RD.' 
          }),
          { 
            status: 503, 
            headers: { 'Content-Type': 'application/json' } 
          }
        );
      })
    );
    return;
  }

  // 3. Recursos públicos y estáticos (HTML, imágenes estáticas, CSS) -> Stale-while-revalidate / Network-first
  event.respondWith(
    caches.match(request).then((cachedResponse) => {
      const fetchPromise = fetch(request).then((networkResponse) => {
        if (networkResponse && networkResponse.status === 200 && networkResponse.type === 'basic') {
          const responseToCache = networkResponse.clone();
          caches.open(CACHE_NAME).then((cache) => {
            cache.put(request, responseToCache);
          });
        }
        return networkResponse;
      }).catch(() => {
        // En caso de estar offline, servir recurso en caché si existe
        return cachedResponse;
      });

      return cachedResponse || fetchPromise;
    })
  );
});
