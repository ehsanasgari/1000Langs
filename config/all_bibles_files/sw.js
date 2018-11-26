webpackJsonp([2],{

/***/ "./resources/assets/js/sw.js":
/***/ (function(module, exports) {

// we'll version our cache (and learn how to delete caches in
// some other post)
var cacheName = 'v1::static';

self.addEventListener('install', function (e) {
    // once the SW is installed, go ahead and fetch the resources
    // to make this work offline
    e.waitUntil(caches.open(cacheName).then(function (cache) {
        return cache.addAll(['/css/app.css', '/js/app.js', '/js/map.js']).then(function () {
            return self.skipWaiting();
        });
    }));
});

// when the browser fetches a url, either response with
// the cached object or go ahead and fetch the actual url
self.addEventListener('fetch', function (event) {
    event.respondWith(
    // ensure we check the *right* cache to match against
    caches.open(cacheName).then(function (cache) {
        return cache.match(event.request).then(function (res) {
            return res || fetch(event.request);
        });
    }));
});

/***/ }),

/***/ 2:
/***/ (function(module, exports, __webpack_require__) {

module.exports = __webpack_require__("./resources/assets/js/sw.js");


/***/ })

},[2]);