import axios from "@agir/lib/utils/axios";
import logger from "@agir/lib/utils/logger";

const log = logger(__filename);

export function loadVersionBrowser() {
  let ua = navigator.userAgent;
  let tem;
  let M =
    ua.match(/(opera|chrome|safari|firefox|msie|trident(?=\/))\/?\s*(\d+)/i) ||
    [];
  if (/trident/i.test(M[1])) {
    tem = /\brv[ :]+(\d+)/g.exec(ua) || [];
    return { name: "IE", version: tem[1] || "" };
  }
  if (M[1] === "Chrome") {
    tem = ua.match(/\bOPR\/(\d+)/);
    if (tem != null) {
      return { name: "Opera", version: tem[1] };
    }
  }
  M = M[2] ? [M[1], M[2]] : [navigator.appName, navigator.appVersion, "-?"];
  if ((tem = ua.match(/version\/(\d+)/i)) != null) {
    M.splice(1, 1, tem[1]);
  }
  return {
    name: M[0],
    version: M[1],
  };
}

function urlBase64ToUint8Array(base64String) {
  var padding = "=".repeat((4 - (base64String.length % 4)) % 4);
  var base64 = (base64String + padding).replace(/-/g, "+").replace(/_/g, "/");

  var rawData = window.atob(base64);
  var outputArray = new Uint8Array(rawData.length);

  for (var i = 0; i < rawData.length; ++i) {
    outputArray[i] = rawData.charCodeAt(i);
  }
  return outputArray;
}

export function getSubscriptionData(pushSubscription) {
  const browser = loadVersionBrowser();
  const endpointParts = pushSubscription.endpoint.split("/");
  const registration_id = endpointParts[endpointParts.length - 1];

  return {
    browser: browser.name.toUpperCase(),
    p256dh: btoa(
      String.fromCharCode(...new Uint8Array(pushSubscription.getKey("p256dh"))),
    ),
    auth: btoa(
      String.fromCharCode(...new Uint8Array(pushSubscription.getKey("auth"))),
    ),
    name: "Action populaire",
    registration_id: registration_id,
  };
}

export async function webpushSubscribe(
  serviceWorkerRegistration,
  pushSubscription,
) {
  if (!process.env.WEBPUSH_PUBLIC_KEY) {
    log.error(
      "WEBPUSH_PUBLIC_KEY must be define. You can generate keys at https://web-push-codelab.glitch.me/.",
    );
  }

  pushSubscription =
    pushSubscription ||
    (await serviceWorkerRegistration.pushManager.subscribe({
      userVisibleOnly: true,
      applicationServerKey: urlBase64ToUint8Array(
        process.env.WEBPUSH_PUBLIC_KEY,
      ),
    })) ||
    (await serviceWorkerRegistration.pushManager.getSubscription());

  if (!pushSubscription) {
    return;
  }

  log.debug("Received PushSubscription: ", pushSubscription);
  return pushSubscription;
}
