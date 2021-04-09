import axios from "@agir/lib/utils/axios";
import logger from "@agir/lib/utils/logger";
import { useCallback, useEffect, useState } from "react";
import { useIOSMessages } from "@agir/front/allPages/ios";
import { doSubscribe } from "@agir/notifications/push/utils";

const log = logger(__filename);

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
