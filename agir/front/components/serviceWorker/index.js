import { matchPrecache, precacheAndRoute } from "workbox-precaching";
import { registerRoute, setCatchHandler } from "workbox-routing";
import { NetworkFirst } from "workbox-strategies";
import hash from "object-hash";
import { CacheableResponsePlugin } from "workbox-cacheable-response";

// Precache assets + offline html page for complete offline app
let webpackAssets = self.__WB_MANIFEST;
webpackAssets.push({
  revision: hash(JSON.stringify(webpackAssets)),
  url: "/offline",
});
precacheAndRoute(webpackAssets);

// Use network first or stale cache for HTML
registerRoute(
  // Check to see if the request is a navigation to a new page
  ({ request }) => request.mode === "navigate",
  new NetworkFirst({
    // Put all cached files in a cache named 'pages'
    cacheName: "pages",
    plugins: [
      // Ensure that only requests that result in a 200 status are cached
      new CacheableResponsePlugin({
        statuses: [200],
      }),
    ],
  })
);

// Use network first or stale cache for some API endpoints
registerRoute(
  "/api/session/",
  new NetworkFirst({
    cacheName: "session",
    plugins: [
      // Ensure that only requests that result in a 200 status are cached
      new CacheableResponsePlugin({
        statuses: [200],
      }),
    ],
  })
);

// If no network and no cache we want to load main app
setCatchHandler(async ({ event }) => {
  // Return the precached offline page if a document is being requested
  if (event.request.destination === "document") {
    return matchPrecache("/offline");
  }

  return Response.error();
});
