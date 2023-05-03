import { setUser as sentrySetUser } from "@sentry/browser";
import { useEffect, useRef } from "react";
import { useLocation } from "react-router-dom";

import { useSelector } from "@agir/front/globalContext/GlobalContext";
import { getUser } from "@agir/front/globalContext/reducers";

const useTracking = () => {
  const location = useLocation();
  const { pathname } = location;
  const previous = useRef(null);
  const user = useSelector(getUser);
  const userId = user?.id || null;

  useEffect(() => {
    if (typeof window !== "undefined" && window._paq) {
      sentrySetUser({ id: userId, ip_address: "{{auto}}" });
      userId
        ? window._paq.push(["setUserId", userId])
        : window._paq.push(["resetUserId"]);
    }
  }, [userId]);

  useEffect(() => {
    if (typeof window !== "undefined" && window._paq) {
      if (previous.current) {
        window._paq.push(["setReferrerUrl", previous.current]);
      }
      previous.current = pathname;
      window._paq.push(["setCustomUrl", pathname]);
      window._paq.push(["trackPageView"]);
      window._paq.push(["HeatmapSessionRecording::enable"]);
    }

    return () => {
      if (typeof window !== "undefined" && window._paq) {
        window._paq.push(["HeatmapSessionRecording::disable"]);
      }
    };
  }, [pathname]);
};

export default useTracking;
