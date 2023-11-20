// public/apiMockServiceWorker.js
self.addEventListener("fetch", (event) => {
  const url = new URL(event.request.url);
  console.log(url.pathname);
  if (!url.pathname.startsWith("/api/")) {
    // Do not propagate this event to other listeners (from MSW)
    event.stopImmediatePropagation();
  }
});

importScripts("./mockServiceWorker.js");
