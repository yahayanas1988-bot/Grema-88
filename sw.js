/* Grema 88 : garde le site disponible même sans connexion. */
var V = "grema88-v7";
var COEUR = ["./", "index.html", "admin.html", "contenu.js", "manifest.webmanifest",
  "images/logo.jpg", "images/partage.jpg", "images/conseil-savane.jpg",
  "images/logo-nessa-tazo-kussa.svg", "images/logo-rdv-pro.svg", "images/icone-192.png", "images/icone-512.png"];
self.addEventListener("install", function (e) {
  e.waitUntil(caches.open(V).then(function (c) { return c.addAll(COEUR); }).then(function () { return self.skipWaiting(); }));
});
self.addEventListener("activate", function (e) {
  e.waitUntil(caches.keys().then(function (k) {
    return Promise.all(k.filter(function (n) { return n !== V; }).map(function (n) { return caches.delete(n); }));
  }).then(function () { return self.clients.claim(); }));
});
self.addEventListener("fetch", function (e) {
  var r = e.request, u = new URL(r.url);
  var police = /^fonts\.(googleapis|gstatic)\.com$/.test(u.hostname);
  if (r.method !== "GET" || (u.origin !== location.origin && !police) || /\.mp4$/.test(u.pathname)) return;
  var html = r.mode === "navigate" || /\.html$|\/$|contenu\.js$/.test(u.pathname);
  if (html) {
    // Pages et contenu : toujours la version la plus récente, sinon la copie gardée.
    e.respondWith(fetch(r).then(function (res) {
      var c = res.clone(); caches.open(V).then(function (k) { k.put(r, c); }); return res;
    }).catch(function () {
      return caches.match(r, {ignoreSearch: true}).then(function (m) { return m || caches.match("index.html"); });
    }));
  } else {
    // Images, polices de la page : la copie gardée d'abord, plus rapide.
    e.respondWith(caches.match(r).then(function (m) {
      return m || fetch(r).then(function (res) {
        if (res.ok || res.type === "opaque") { var c = res.clone(); caches.open(V).then(function (k) { k.put(r, c); }); }
        return res;
      });
    }));
  }
});
