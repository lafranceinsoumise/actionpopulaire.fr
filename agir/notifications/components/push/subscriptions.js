import axios from "@agir/lib/utils/axios";
import logger from "@agir/lib/utils/logger";
import { useCallback, useEffect, useState } from "react";
import { useIOSMessages } from "@agir/front/allPages/ios";

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

async function doSubscribe(serviceWorkerRegistration) {
  if (!process.env.WEBPUSH_PUBLIC_KEY) {
    log.error(
      "WEBPUSH_PUBLIC_KEY must be define. You can generate keys at https://web-push-codelab.glitch.me/."
    );
  }
  const pushSubscription = await serviceWorkerRegistration.pushManager.subscribe(
    {
      userVisibleOnly: true,
      applicationServerKey: urlBase64ToUint8Array(
        process.env.WEBPUSH_PUBLIC_KEY
      ),
    }
  );

  log.debug("Received PushSubscription: ", pushSubscription);

  const browser = loadVersionBrowser();

  const endpointParts = pushSubscription.endpoint.split("/");
  const registration_id = endpointParts[endpointParts.length - 1];
  const data = {
    browser: browser.name.toUpperCase(),
    p256dh: btoa(
      String.fromCharCode(...new Uint8Array(pushSubscription.getKey("p256dh")))
    ),
    auth: btoa(
      String.fromCharCode(...new Uint8Array(pushSubscription.getKey("auth")))
    ),
    name: "Action populaire",
    registration_id: registration_id,
  };

  try {
    await axios.post("/api/device/webpush/", data);
  } catch (e) {
    log.error("Error saving PushSubscription : ", e);
  }
  log.debug("Save PushSubscription");

  return pushSubscription;
}

async function askPermission() {
  let permissionResult = await new Promise((resolve, reject) => {
    const permissionPromise = Notification.requestPermission(function (result) {
      resolve(result);
    });

    if (permissionPromise) {
      permissionPromise.then(resolve, reject);
    }
  });

  if (permissionResult !== "granted") {
    throw new Error("We weren't granted permission.");
  }
}

const useWebPush = () => {
  const [ready, setReady] = useState(false);
  const [isSubscribed, setIsSubscribed] = useState(false);

  const subscribe = useCallback(async () => {
    await askPermission();
    await doSubscribe(window.AgirSW);
    setIsSubscribed(true);
  }, []);

  useEffect(() => {
    (async () => {
      if (!window.AgirSW?.pushManager || ready) return;

      const pushSubscription = await window.AgirSW?.pushManager?.getSubscription();

      if (!pushSubscription) {
        setReady(true);
        return;
      }

      const endpointParts = pushSubscription.endpoint.split("/");
      const registrationId = endpointParts[endpointParts.length - 1];

      try {
        await axios(`/api/device/webpush/${registrationId}/`);
        setIsSubscribed(true);
        setReady(true);
      } catch (e) {
        if (e.response?.status === 404) {
          log.debug("Registration did not exist on server, unsubscribe.");
          await pushSubscription.unsubscribe();
          setIsSubscribed(false);
        } else {
          log.error(e);
        }

        setReady(true);
      }
    })();
  }, [ready]);

  if (!window.AgirSW || !window.AgirSW.pushManager) {
    log.debug("Push manager not available.");

    return {
      ready: true,
      available: false,
    };
  }

  if (!ready) {
    return {
      ready: false,
    };
  }

  return {
    ready: true,
    available: true,
    isSubscribed: isSubscribed,
    subscribe,
  };
};

const useIOSPush = () => {
  const [ready, setReady] = useState(false);
  const [isSubscribed, setIsSubscribed] = useState(false);

  // We change state when iOS app send information
  const messageHandler = useCallback(async (data) => {
    if (data.action !== "setNotificationState") {
      return;
    }

    if (data.noPermission) {
      setReady(true);
      return;
    }

    try {
      await axios.post("/api/device/apple/", {
        name: "Action populaire",
        registration_id: data.token,
      });
      setReady(true);
      setIsSubscribed(true);
    } catch (e) {
      log.error("Error saving Apple push subscription : ", e);
    }
  }, []);
  const postMessage = useIOSMessages(messageHandler);

  useEffect(() => {
    postMessage && postMessage({ action: "getNotificationState" });
  }, [postMessage]);

  const subscribe = useCallback(() => {
    postMessage && postMessage({ action: "enableNotifications" });
  }, [postMessage]);

  // Not on iOSDevice
  if (!postMessage) {
    return {
      ready: true,
      available: false,
    };
  }

  // iOS device but no info yet about subscription
  if (!ready) {
    return {
      ready: false,
    };
  }

  return {
    ready: true,
    available: true,
    isSubscribed: isSubscribed,
    subscribe,
  };
};

export const usePush = () => {
  const iosPush = useIOSPush();
  const webPush = useWebPush();

  if (iosPush.ready && iosPush.available) {
    return iosPush;
  }

  if (webPush.ready && webPush.available) {
    return webPush;
  }

  return {
    ready: iosPush.ready && webPush.ready,
    available: false,
  };
};
