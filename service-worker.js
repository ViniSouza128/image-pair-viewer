/* =====================================================================
   image-pair-viewer — Service Worker

   Estratégia: cache da "shell" (index.html + manifest + ícones) na
   instalação, depois cache-first pra estáticos e network-first pra
   HTML. Resultado prático:

     - 1º acesso ONLINE: tudo é cacheado.
     - Acessos seguintes: shell servida do cache (instantâneo).
     - Update do index.html: detectado na próxima vez que houver rede;
       SW pega versão nova em background, próxima abertura usa a nova.
     - OFFLINE: app abre normalmente, processa fotos locais como sempre.
                Sample images abrem se já tinham sido visitadas alguma vez.

   IMPORTANTE — a aplicação NÃO depende do SW pra funcionar. O SW só
   acelera carregamento e habilita modo offline. Se ele falhar ou for
   desregistrado, o app continua funcionando 100% como antes.

   Versionamento: incremente CACHE_VERSION quando precisar forçar uma
   re-instalação completa dos assets cacheados (geralmente após mudança
   de shell ou de ícones).
   ===================================================================== */

const CACHE_VERSION = 'v1';
const CACHE_NAME = 'ipv-' + CACHE_VERSION;

/* SHELL — arquivos pré-cacheados na instalação.
   Cobre o que é necessário pra abrir o app vazio offline. Samples
   ficam de fora pra não inflar o install (3.6 MB) — eles entram no
   cache automaticamente quando o usuário clica em "Experimentar". */
const SHELL = [
  './',
  './index.html',
  './manifest.webmanifest',
  './icons/icon-192.png',
  './icons/icon-512.png',
  './icons/icon-180.png',
  './icons/icon-maskable-512.png',
];

/* INSTALL — abre o cache e baixa a shell.
   skipWaiting() faz o SW novo ativar imediatamente (sem esperar abas
   antigas fecharem). Importante pra usuário receber updates rápido. */
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => cache.addAll(SHELL))
      .then(() => self.skipWaiting())
  );
});

/* ACTIVATE — apaga caches de versões antigas.
   clients.claim() faz este SW assumir o controle das abas já abertas
   sem precisar de reload. */
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(
        keys
          .filter((k) => k.startsWith('ipv-') && k !== CACHE_NAME)
          .map((k) => caches.delete(k))
      )
    ).then(() => self.clients.claim())
  );
});

/* FETCH — roteamento por tipo de requisição.

   1. Métodos não-GET (POST etc.): bypass total — não cacheamos.
   2. Cross-origin (Nominatim, Wikimedia, etc.): bypass — deixa o
      browser fazer. Reverse-geocoding é dinâmico e externo.
   3. Navegação (request mode=navigate / destination=document):
      network-first. Garante que update do index.html chega rápido.
      Fallback no cache se offline.
   4. Tudo mais (CSS in-line não existe aqui, então isso é icons,
      manifest, samples, etc.): cache-first.
*/
self.addEventListener('fetch', (event) => {
  const req = event.request;
  if (req.method !== 'GET') return;

  const url = new URL(req.url);
  if (url.origin !== self.location.origin) return;  // cross-origin: passa direto

  // Navegação / documento HTML: network-first com fallback no cache.
  if (req.mode === 'navigate' || req.destination === 'document') {
    event.respondWith(networkFirst(req));
    return;
  }

  // Estáticos same-origin (icons, manifest, samples, etc.): cache-first.
  event.respondWith(cacheFirst(req));
});

/* network-first — tenta rede primeiro, atualiza o cache, e cai no cache
   se a rede falhar. Para HTML, é o equilíbrio certo entre "ver a versão
   mais nova" e "funcionar offline". */
async function networkFirst(req) {
  const cache = await caches.open(CACHE_NAME);
  try {
    const fresh = await fetch(req);
    // Só cacheia respostas válidas (200) — não cacheia 404/5xx.
    if (fresh && fresh.ok) {
      cache.put(req, fresh.clone());
    }
    return fresh;
  } catch (err) {
    const cached = await cache.match(req);
    if (cached) return cached;
    // Último fallback: pelo menos a raiz cacheada (resolve "abriu offline
    // direto numa URL profunda" → mostra o app vazio em vez de erro).
    const rootFallback = await cache.match('./index.html') || await cache.match('./');
    if (rootFallback) return rootFallback;
    return new Response('Offline', { status: 503, statusText: 'Offline' });
  }
}

/* cache-first — devolve do cache se tiver; senão busca na rede, cacheia
   e devolve. Estratégia ideal pra assets versionados/imutáveis. */
async function cacheFirst(req) {
  const cache = await caches.open(CACHE_NAME);
  const cached = await cache.match(req);
  if (cached) return cached;
  try {
    const fresh = await fetch(req);
    if (fresh && fresh.ok) {
      cache.put(req, fresh.clone());
    }
    return fresh;
  } catch (err) {
    // Sem rede + sem cache: devolve um 503 silencioso. O app trata o
    // erro de fetch dele mesmo (mostra mensagem no #uploadError).
    return new Response('', { status: 503, statusText: 'Offline' });
  }
}

/* MENSAGENS — permite à página pedir um update imediato (futuro).
   Ex.: ao detectar que há um SW novo aguardando, mandar 'SKIP_WAITING'
   pra ele ativar sem reload manual. */
self.addEventListener('message', (event) => {
  if (event.data === 'SKIP_WAITING') {
    self.skipWaiting();
  }
});
