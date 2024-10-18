import {useCallback, useEffect, useRef, useState} from "react";

import logger from "@agir/lib/utils/logger";

const log = logger(__filename);

window.iOSNativeMessage = (data) => {
  let event = new CustomEvent("iOSMessage", {
    detail: {
      data: JSON.parse(data),
    },
  });

  log.debug("got message", data);

  window.dispatchEvent(event);
};

const iosAction= {
  SET_NOTIFICATION_STATE: 'setNotificationState',
  GET_NOTIFICATION_STATE: 'getNotificationState',
  ENABLE_NOTIFICATIONS: 'enableNotifications'
};

export const useIOSNotificationGrant = () => {
  const [notificationIsGranted, setNotificationIsGranted] = useState(false)

  const iosMessageHandler = useCallback(async ({action, noPermission}) => {
    console.log('event', action, noPermission)
    if (action === iosAction.SET_NOTIFICATION_STATE && noPermission === "false") {
      setNotificationIsGranted(true);
    }
  }, []);

  const postMessage = useIOSMessages(iosMessageHandler);

  useEffect(() => {
    postMessage && postMessage({ action: iosAction.GET_NOTIFICATION_STATE });
  }, [postMessage]);

  const grantNotification = useCallback(() => {
    if (postMessage) {
      postMessage && postMessage({ action: iosAction.ENABLE_NOTIFICATIONS });
    } else {
      console.error("postMessage not found !")
    }
  }, [postMessage])

  return {
    grantNotification,
    notificationIsGranted
  }
}

export const useIOSMessages = (cb) => {
  const savedCallback = useRef();

  useEffect(() => {
    savedCallback.current = cb;
  }, [cb]);

  useEffect(() => {
    const eventListener = (event) =>
      savedCallback.current && savedCallback.current(event.detail.data);

    window.addEventListener("iOSMessage", eventListener);

    return () => {
      window.removeEventListener("iOSMessage", eventListener);
    };
  }, []);

  const postMessage = useCallback((data) => {
    window.webkit?.messageHandlers?.main?.postMessage(data);
  }, []);

  if (!window.webkit?.messageHandlers?.main) {
    return;
  }

  return postMessage;
};
