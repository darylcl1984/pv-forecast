// v5 — 2026-09-05
const CACHE_NAME = 'solar-forecast-v5';

const SHELL_ASSETS = [
  './',
  './index.html',
  './manifest.json',
  './icons/icon-48.png',
  './icons/icon-72.png',
  './icons/icon-96.png',
  './icons/icon-144.png',
  './icons/icon-192.png',
  './icons/icon-512.png'
];

// CDN assets — versioned/immutable, safe to cache-first indefinitely
const CDN_ASSETS = [
  'https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js',
  'https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&family=IBM+Plex+Mono:wght@400;500&family=Space+Grotesk:wght@400;500&display=swap'
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => Promise.allSettled(
        [...SHELL_ASSETS, ...CDN_ASSETS].map(url => cache.add(url))
      ))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', event => {
  event.waitUntil((async () => {
    const cache = await caches.open(CACHE_NAME);
    const hasShell = await cache.match('./') || await cache.match('./index.html');
    // Keep the previous cache if this version never stored a document —
    // otherwise a bump while offline bricks the installed app.
    if (hasShell) {
      const keys = await caches.keys();
      await Promise.all(keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k)));
    }
    await self.clients.claim();
  })());
});

self.addEventListener('fetch', event => {
  // Pass forecast / geocoding API calls straight through
  if (event.request.url.includes('open-meteo.com')) return;
  if (event.request.url.includes('photon.komoot.io')) return;

  const url = new URL(event.request.url);
  const isNavigate = event.request.mode === 'navigate'
    || event.request.destination === 'document'
    || url.pathname.endsWith('index.html');

  // Network-first for navigations (GitHub Pages lives at /pv-forecast/, not /)
  if (isNavigate) {
    event.respondWith(
      fetch(event.request)
        .then(response => {
          if (response.ok) {
            const clone = response.clone();
            caches.open(CACHE_NAME).then(cache => cache.put(event.request, clone));
          }
          return response;
        })
        .catch(() => caches.match(event.request)
          .then(cached => cached || caches.match('./index.html') || caches.match('./')))
    );
    return;
  }

  // Cache-first for CDN / static assets — with offline fallback
  event.respondWith(
    caches.match(event.request).then(cached => {
      if (cached) return cached;
      return fetch(event.request).then(response => {
        if (response.ok && response.type !== 'opaque') {
          const clone = response.clone();
          caches.open(CACHE_NAME).then(cache => cache.put(event.request, clone));
        }
        return response;
      }).catch(() => caches.match(event.request));
    })
  );
});
