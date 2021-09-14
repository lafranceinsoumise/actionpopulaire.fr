import { useCallback, useEffect, useMemo, useState } from "react";

import axios from "@agir/lib/utils/axios";
import logger from "@agir/lib/utils/logger";
import { useIOSMessages } from "@agir/front/allPages/ios";
import { useMobileApp } from "@agir/front/app/hooks";
import { useLocalStorage } from "@agir/lib/utils/hooks";

const log = logger(__filename);

const SUBSCRIPTION_TYPES = {
  ANDROID: "android",
  APPLE: "apple",
  WEBPUSH: "webpush",
};

const useServerSubscription = (endpoint, token) => {
  const [ready, setReady] = useState(false);
  const [isSubscribed, setIsSubscribed] = useState(false);
  const [registration_id, extraData] = useMemo(
    () =>
      !token || typeof token === "string"
        ? [token, {}]
        : [token.registration_id, token],
    [token]
  );

  const subscribe = useCallback(async () => {
    try {
      await axios.post(`/api/device/${endpoint}/`, {
        name: "Action populaire",
        registration_id: registration_id,
        active: true,
        ...extraData,
      });
      setReady(true);
      setIsSubscribed(true);
    } catch (e) {
      log.error(`Error saving ${endpoint} push subscription : `, e);
      setReady(true);
      setIsSubscribed(false);
    }
  }, [endpoint, extraData, registration_id]);

  const unsubscribe = useCallback(async () => {
    if (!registration_id) {
      return;
    }
    let isUnsubscribed = false;
    try {
      log.debug(`${endpoint} : error disabling device`, registration_id);
      await axios.put(`/api/device/${endpoint}/${registration_id}/`, {
        registration_id: registration_id,
        active: false,
      });
      isUnsubscribed = true;
    } catch (e) {
      log.error("iOS: Error disabling push subscription : ", e);
      isUnsubscribed = e.response?.status === 404;
    }
    if (isUnsubscribed) {
      log.debug("iOS : device unsubscribed", registration_id);
      setIsSubscribed(false);
    }
  }, [endpoint, registration_id]);

  // When receive a new token, if it does not exist, we subscribe by default
  useEffect(() => {
    (async () => {
      if (!registration_id) {
        return;
      }

      log.debug("Notifications : got token ", registration_id);

      let deviceSubscription = null;
      try {
        deviceSubscription = await axios(
          `/api/device/${endpoint}/${registration_id}/`
        );
      } catch (e) {
        if (e.response?.status === 404) {
          await subscribe();
        }

        log.error("Error retrieving subscription", registration_id, e);

        setReady(true);
        return;
      }

      // Check if subscription for the current token exists and is active
      setReady(true);
      setIsSubscribed(deviceSubscription.data.active);
    })();
  }, [endpoint, registration_id, subscribe]);

  return {
    ready,
    isSubscribed,
    subscribe,
    unsubscribe,
  };
};

const useAndroidPush = () => {
  const { isAndroid } = useMobileApp();
  const [token] = useLocalStorage("AP_FCMToken", null, { raw: true });

  const { ready, isSubscribed, subscribe, unsubscribe } = useServerSubscription(
    SUBSCRIPTION_TYPES.ANDROID,
    token && {
      registration_id: token,
      cloud_message_type: "FCM",
    }
  );

  if (!isAndroid) {
    log.debug("Android : not on Android device.");
    return {
      ready: true,
      available: false,
    };
  }

  if (!token) {
    log.debug("Android : not ready.");
    return {
      ready: false,
    };
  }

  return {
    ready,
    available: true,
    isSubscribed,
    subscribe,
    unsubscribe: isSubscribed ? unsubscribe : undefined,
  };
};

const useIOSPush = () => {
  const [phoneReady, setPhoneReady] = useState(false);
  const [subscriptionToken, setSubscriptionToken] = useState(null);

  const {
    ready: serverReady,
    isSubscribed,
    subscribe: serverSubscribe,
    unsubscribe,
  } = useServerSubscription("apple", subscriptionToken);

  // We change state when iOS app send information
  const messageHandler = useCallback(async (data) => {
    log.debug("iOS : got message", data);

    if (data.action !== "setNotificationState") {
      return;
    }

    setPhoneReady(true);

    if (data.noPermission) {
      log.debug("iOS : no notification permission");
      return;
    }

    if (data.token) {
      setSubscriptionToken(data.token);
    }
  }, []);

  const postMessage = useIOSMessages(messageHandler);

  useEffect(() => {
    postMessage && postMessage({ action: "getNotificationState" });
  }, [postMessage]);

  const subscribe = useCallback(async () => {
    if (subscriptionToken) {
      return await serverSubscribe(subscriptionToken);
    }

    postMessage && postMessage({ action: "enableNotifications" });
  }, [postMessage, serverSubscribe, subscriptionToken]);

  // Not on iOSDevice
  if (!postMessage) {
    log.debug("iOS : not on iOS device.");
    return {
      ready: true,
      available: false,
    };
  }

  // iOS device but no info yet about subscription
  if (!phoneReady) {
    log.debug("iOS : waiting for iOS informations");
    return {
      ready: false,
    };
  }

  // iOS device but no permission
  if (!subscriptionToken) {
    log.debug("iOS : no permisson");
    return {
      ready: true,
      available: false,
      errorMessage: "Veuillez activer la permisson pour les notifications.",
    };
  }

  log.debug("iOS : isSubscribed ", isSubscribed);
  return {
    ready: serverReady,
    available: true,
    isSubscribed,
    subscribe,
    unsubscribe: isSubscribed ? unsubscribe : undefined,
  };
};

export const usePush = () => {
  const iosPush = useIOSPush();
  const androidPush = useAndroidPush();

  if (iosPush.ready && iosPush.available) {
    return iosPush;
  }

  if (androidPush.ready && androidPush.available) {
    return androidPush;
  }

  return {
    ready: iosPush.ready && androidPush.ready,
    available: false,
  };
};
