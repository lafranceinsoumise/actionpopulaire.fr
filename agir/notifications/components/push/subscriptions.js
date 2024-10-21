import { useCallback, useEffect, useMemo, useState } from "react";

import logger from "@agir/lib/utils/logger";
import { useIOSMessages } from "@agir/front/allPages/ios";
import { useMobileApp } from "@agir/front/app/hooks";
import { useLocalStorage } from "@agir/lib/utils/hooks";

const log = logger(__filename);

import * as API from "./api";

const useServerSubscription = (deviceType, token) => {
  const [ready, setReady] = useState(false);
  const [isSubscribed, setIsSubscribed] = useState(false);

  const subscribe = useCallback(async () => {
    if (!ready && token) {
      const isSubscribed = await API.subscribe(deviceType, token);
      setReady(true);
      setIsSubscribed(isSubscribed);
    }
  }, [deviceType, token]);

  const unsubscribe = useCallback(async () => {
    if (!token) {
      return;
    }
    const isUnsubscribed = await API.unsubscribe(deviceType, token);
    setIsSubscribed(isUnsubscribed);
  }, [deviceType, token]);

  useEffect(() => {
    (async () => {
      if (!token) {
        return;
      }
      const isSubscribed = await API.getSubscription(deviceType, token);
      if (typeof isSubscribed !== "boolean") {
        subscribe();
        return;
      }
      setReady(true);
      setIsSubscribed(isSubscribed);
    })();
  }, [deviceType, token, subscribe]);

  const state = useMemo(
    () => ({
      ready,
      isSubscribed,
      subscribe,
      unsubscribe,
    }),
    [ready, isSubscribed, subscribe, unsubscribe],
  );

  return state;
};

const useAndroidPush = () => {
  const { isAndroid } = useMobileApp();
  const [token, setToken, removeToken, refreshToken] = useLocalStorage("AP_FCMToken", null);

  const { ready, isSubscribed, subscribe, unsubscribe } = useServerSubscription(
    API.DEVICE_TYPE.ANDROID,
    token,
  );

  const state = useMemo(() => {
    if (!isAndroid) {
      log.debug(`${API.DEVICE_TYPE.ANDROID}: Not an Android device`);
      return {
        ready: true,
        available: false,
      };
    }

    if (!token) {
      log.debug(`${API.DEVICE_TYPE.ANDROID}: Missing token for Android device`);
      return {
        ready: false,
        refreshToken
      };
    }

    log.debug(`${API.DEVICE_TYPE.ANDROID}: Subscription active?`, isSubscribed);
    return {
      ready,
      available: true,
      isSubscribed,
      subscribe,
      unsubscribe: isSubscribed ? unsubscribe : undefined,
      refreshToken
    };
  }, [isAndroid, ready, isSubscribed, subscribe, unsubscribe]);

  return state;
};

const useIOSPush = () => {
  const [phoneReady, setPhoneReady] = useState(false);
  const [subscriptionToken, setSubscriptionToken, removeToken, refreshToken] =  useLocalStorage("AP_FCMToken", null);

  const {
    ready: serverReady,
    isSubscribed,
    subscribe,
    unsubscribe,
  } = useServerSubscription(API.DEVICE_TYPE.IOS, subscriptionToken);

  const state = useMemo(() => {
    // Not on iOSDevice
    if (!postMessage) {
      log.debug(`${API.DEVICE_TYPE.IOS}: Not an IOS device`);
      return {
        ready: true,
        available: false,
        refreshToken
      };
    }

    // iOS device but no info yet about subscription
    if (!phoneReady) {
      log.debug(
        `${API.DEVICE_TYPE.IOS}: Waiting for IOS device subscription status`,
      );
      return {
        ready: false,
        refreshToken,
      };
    }

    // iOS device but no permission
    if (!subscriptionToken) {
      log.debug(`${API.DEVICE_TYPE.IOS}: Missing permissions`);
      return {
        ready: true,
        available: false,
        refreshToken
      };
    }

    log.debug(`${API.DEVICE_TYPE.IOS}: Subscription active?`, isSubscribed);
    return {
      ready: serverReady,
      available: true,
      isSubscribed,
      subscribe,
      refreshToken,
      unsubscribe: isSubscribed ? unsubscribe : undefined,
    };
  }, [
    refreshToken,
    postMessage,
    phoneReady,
    subscriptionToken,
    serverReady,
    isSubscribed,
    subscribe,
    unsubscribe,
  ]);

  return state;
};

export const usePush = () => {
  const iosPushState = useIOSPush();
  const androidPushState = useAndroidPush();

  const state = useMemo(() => {
    let currentState = {
      ready: iosPushState.ready || androidPushState.ready,
      available: false,
      refreshToken: () => { iosPushState.refreshToken?.();  androidPushState.refreshToken?.() }
    };
    if (iosPushState.ready && iosPushState.available) {
      currentState = iosPushState;
    }
    if (androidPushState.ready && androidPushState.available) {
      currentState = androidPushState;
    }

    log.debug("Push notifications' current state", currentState);

    return currentState;
  }, [iosPushState, androidPushState]);

  return state;
};
