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
};

export const useIOSNotificationGrant = () => {
  const [notificationIsGranted, setNotificationIsGranted] = useState(false)

  const iosMessageHandler = useCallback(async (data) => {
    if (data.action === iosAction.SET_NOTIFICATION_STATE && !data.noPermission) {
      setNotificationIsGranted(true);
    }
  }, []);

  const postMessage = useIOSMessages(iosMessageHandler);

  const grantNotification = useCallback(() => {
    if (postMessage) {
      postMessage && postMessage({ action: "enableNotifications" });
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
