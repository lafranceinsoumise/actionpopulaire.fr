/* eslint-env serviceworker */

import { webpushSubscribe } from "@agir/notifications/push/webpushUtils";

import DEFAULT_ICON from "@agir/front/genericComponents/logos/action-populaire_mini.svg";
import NOTIFICATION_BADGE from "@agir/front/genericComponents/logos/notification-badge.png";

const DEFAULT_URL = "/activite/";
const DEFAULT_TITLE = "Action Populaire";

const doDisplayNotification = async function (message) {
  if (!message || !message.body) {
    return;
  }
  return self.registration.showNotification(message.title || DEFAULT_TITLE, {
    body: message.body,
    badge: NOTIFICATION_BADGE,
    icon: message.icon || DEFAULT_ICON,
    tag: message.tag,
    data: { url: message.url || DEFAULT_URL },
  });
};

self.addEventListener("push", function (event) {
  let message = "";
  try {
    message = event.data.json();
  } catch (e) {
    message = {
      body: event.data.text(),
    };
  }
  /* callback for push event must be synced, and event must be attached
     to a promise if no notification has been displayed when promise returns,
     the broswer issues an (ugly) warning that data has been sent in background
   */
  event.waitUntil(doDisplayNotification(message));
});

self.addEventListener(
  "notificationclick",
  function (event) {
    event.notification.close();
    event.waitUntil(
      clients
        .matchAll({ type: "window", includeUncontrolled: true })
        .then(function (windowClients) {
          const url = event.notification.data.url || DEFAULT_URL;
          let hasClient = false;
          for (let i = 0; !hasClient && windowClients[i]; i++) {
            if (
              windowClients[i].url.endsWith(url) &&
              "focus" in windowClients[i]
            ) {
              hasClient = true;
              return windowClients[i].focus();
            }
          }
          if (!hasClient) {
            clients.openWindow(url);
          }
        }),
    );
  },
  false,
);

self.addEventListener(
  "pushsubscriptionchange",
  function (event) {
    event.waitUntil(webpushSubscribe(self.registration, event.newSubscription));
  },
  false,
);
