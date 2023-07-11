import { matchPrecache, precacheAndRoute } from "workbox-precaching";
import { registerRoute, setCatchHandler } from "workbox-routing";
import { NetworkFirst, NetworkOnly } from "workbox-strategies";
import hash from "object-hash";
import { CacheableResponsePlugin } from "workbox-cacheable-response";

import { ExpirationPlugin } from "workbox-expiration";

import cachedRoutes from "./cachedRoutes.config";

// Precache assets + offline html page for complete offline app
let webpackAssets = self.__WB_MANIFEST;
webpackAssets.unshift({
  revision: hash(JSON.stringify(webpackAssets)),
  url: "/offline",
});
precacheAndRoute(webpackAssets);

// Use network only for HTML and for pinging the API
registerRoute(
  // Check to see if the request is a navigation to a new page
  ({ request }) => request.mode === "navigate",
  new NetworkOnly(),
);

// Use network first or stale cache for some API endpoints
const apiStrategy = new NetworkFirst({
  cacheName: "session",
  plugins: [
    // Ensure that only requests that result in a 200 status are cached
    new CacheableResponsePlugin({
      statuses: [200],
    }),
    new ExpirationPlugin({
      maxAgeSeconds: 24 * 60 * 60,
    }),
  ],
});
cachedRoutes.map((route) => registerRoute(route, apiStrategy));

// If no network and no cache we want to load main app
setCatchHandler(async ({ event }) => {
  // Return the precached offline page if a document is being requested
  if (event.request.destination === "document") {
    return matchPrecache("/offline");
  }

  return Response.error();
});

import "./notificationsDisplay";
