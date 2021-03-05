import { useCallback, useEffect, useRef, useState } from "react";
import useSWR from "swr";

export const useIsOffline = () => {
  const { data, error, isValidating } = useSWR("/api/session");
  const [isOffline, setIsOffline] = useState(false);
  const timeout = useRef(null);
  const clear = useCallback(() => {
    if (timeout.current) {
      clearTimeout(timeout.current);
      timeout.current = null;
    }
  }, [timeout]);
  useEffect(() => {
    const isOffline = !data && !error && isValidating ? null : !!error;

    if (isOffline !== false) {
      setIsOffline(isOffline);
    } else {
      timeout.current = setTimeout(() => {
        setIsOffline(isOffline);
      }, 1000);
    }

    return clear;
  }, [clear, data, error, isValidating]);

  return isOffline;
};
