import axios from "@agir/lib/utils/axios";
import logger from "@agir/lib/utils/logger";
import { useCallback, useEffect, useState } from "react";
import { useIOSMessages } from "@agir/front/allPages/ios";
import { doSubscribe, doUnsubscribe } from "@agir/notifications/push/utils";

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
  const [errorMessage, setErrorMessage] = useState("");

  const subscribe = useCallback(async () => {
    setErrorMessage("");
    await askPermission();
    const subscription = await doSubscribe(window.AgirSW);
    if (!subscription) {
      setIsSubscribed(false);
      setErrorMessage("Une erreur est survenue.");
    } else {
      setIsSubscribed(true);
    }
  }, []);

  const unsubscribe = useCallback(async () => {
    const success = await doUnsubscribe();
    if (success) {
      setIsSubscribed(false);
    }
  }, []);

  const init = useCallback(async (serviceWorker) => {
    if (!serviceWorker?.pushManager) {
      setReady(true);
      setIsSubscribed(false);
      return;
    }

    const pushSubscription = await serviceWorker.pushManager.getSubscription();

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
  }, []);

  useEffect(() => {
    let serviceWorker;
    let handleStateChange;

    if (window.AgirSW?.installing) {
      serviceWorker = window.AgirSW.installing;
    } else if (window.AgirSW?.waiting) {
      serviceWorker = window.AgirSW.waiting;
    } else if (window.AgirSW?.active) {
      serviceWorker = window.AgirSW.active;
    }

    if (serviceWorker && window.AgirSW.pushManager && !ready) {
      if (serviceWorker.state === "activated") {
        init(window.AgirSW);
      } else {
        handleStateChange = (e) => {
          e.target.state === "activated" && init(window.AgirSW);
        };
        serviceWorker.addEventListener("statechange", handleStateChange);
      }
    }

    return () => {
      serviceWorker &&
        handleStateChange &&
        serviceWorker.removeEventListener("statechange", handleStateChange);
    };
  }, [init, ready]);

  if (!window.AgirSW || !window.AgirSW.pushManager) {
    log.debug("Web PushManager not available.");

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
    unsubscribe: isSubscribed ? unsubscribe : undefined,
    errorMessage,
  };
};

const useIOSPush = () => {
  const [ready, setReady] = useState(false);
  const [isSubscribed, setIsSubscribed] = useState(false);
  const [subscriptionToken, setSubscriptionToken] = useState(null);

  const registerDevice = useCallback(async (token) => {
    try {
      await axios.post("/api/device/apple/", {
        name: "Action populaire",
        registration_id: token,
        active: true,
      });
      setReady(true);
      setIsSubscribed(true);
      setSubscriptionToken(token);
    } catch (e) {
      log.error("iOS : error saving Apple push subscription : ", e);
      setReady(true);
      setIsSubscribed(false);
    }
  }, []);

  // We change state when iOS app send information
  const messageHandler = useCallback(
    async (data) => {
      log.debug("iOS : got message", data);

      if (data.action !== "setNotificationState") {
        return;
      }

      if (data.noPermission) {
        log.debug("iOS : no notification permission");
        setReady(true);
        return;
      }

      let deviceSubscription = null;
      try {
        deviceSubscription = await axios(`/api/device/webpush/${data.token}/`);
      } catch (e) {
        if (e.response?.status !== 404) {
          setReady(true);
          log.error("iOS: error retrieving subscription", data.token, e);
          return;
        }
        deviceSubscription = null;
      }

      if (deviceSubscription) {
        // Check if subscription for the current token exists and is active
        setReady(true);
        setIsSubscribed(deviceSubscription.active);
        setSubscriptionToken(data.token);
        return;
      }

      registerDevice(data.token);
    },
    [registerDevice]
  );

  const postMessage = useIOSMessages(messageHandler);

  useEffect(() => {
    postMessage && postMessage({ action: "getNotificationState" });
  }, [postMessage]);

  const subscribe = useCallback(() => {
    if (subscriptionToken) {
      registerDevice(subscriptionToken);
    } else {
      postMessage && postMessage({ action: "enableNotifications" });
    }
  }, [postMessage, registerDevice, subscriptionToken]);

  const unsubscribe = useCallback(async () => {
    if (!subscriptionToken) {
      return;
    }
    let isUnsubscribed = false;
    try {
      log.debug("iOS : disabling device", subscriptionToken);
      await axios.put(`/api/device/webpush/${subscriptionToken}/`, {
        registration_id: subscriptionToken,
        active: false,
      });
      isUnsubscribed = true;
    } catch (e) {
      log.error("iOS: Error disabling push subscription : ", e);
      isUnsubscribed = e.response?.status === 404;
    }
    if (isUnsubscribed) {
      log.debug("iOS : device unsubscribed", subscriptionToken);
      setIsSubscribed(false);
    }
  }, [subscriptionToken]);

  // Not on iOSDevice
  if (!postMessage) {
    log.debug("iOS : not on iOS device.");
    return {
      ready: true,
      available: false,
    };
  }

  // iOS device but no info yet about subscription
  if (!ready) {
    log.debug("iOS : waiting for iOS informations");
    return {
      ready: false,
    };
  }

  log.debug("iOS : isSubscribed ", isSubscribed);
  return {
    ready: true,
    available: true,
    isSubscribed,
    subscribe,
    unsubscribe: isSubscribed ? unsubscribe : undefined,
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
