/* Service worker kecil: menambahkan header COOP/COEP pada semua respons
   halaman ini agar browser mengizinkan SharedArrayBuffer (isolasi
   cross-origin) yang dibutuhkan mesin WebAssembly bertali banyak. */
self.addEventListener("install", () => self.skipWaiting());
self.addEventListener("activate", (e) => e.waitUntil(self.clients.claim()));
self.addEventListener("fetch", (e) => {
  if (e.request.cache === "only-if-cached" && e.request.mode !== "same-origin") return;
  e.respondWith(
    fetch(e.request)
      .then((r) => {
        if (r.status === 0) return r;
        const h = new Headers(r.headers);
        h.set("Cross-Origin-Embedder-Policy", "require-corp");
        h.set("Cross-Origin-Opener-Policy", "same-origin");
        return new Response(r.body, { status: r.status, statusText: r.statusText, headers: h });
      })
      .catch((err) => err),
  );
});
