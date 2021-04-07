import { useCallback, useEffect, useRef } from "react";

window.iOSNativeMessage = (data) => {
  let event = new CustomEvent("iOSMessage", {
    detail: {
      data,
    },
  });

  window.dispatchEvent(event);
};

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
