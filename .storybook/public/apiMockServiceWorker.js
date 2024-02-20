// public/apiMockServiceWorker.js

const API_PATHNAME_PREFIXES = ["/api/", "/data-france/"];
self.addEventListener("fetch", (event) => {
  const url = new URL(event.request.url);
  if (
    !API_PATHNAME_PREFIXES.some((prefix) => url.pathname.startsWith(prefix))
  ) {
    // Do not propagate this event to other listeners (from MSW)
    event.stopImmediatePropagation();
  }
});

importScripts("./mockServiceWorker.js");
