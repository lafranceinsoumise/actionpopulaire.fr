import { useEffect, useState } from "react";
import useSWR from "swr";

import logger from "@agir/lib/utils/logger";

const log = logger(__filename);

export const useIsOffline = () => {
  const { data, error, isValidating } = useSWR("/api/session/");
  const [unloading, setUnloading] = useState(false);

  log.debug(`Unloading : ${unloading}`, unloading);
  if (error) {
    log.debug(`Error : ${error}`, error);
  }

  useEffect(() => {
    let cb = () => setUnloading(true);
    window.addEventListener("beforeunload", cb);

    return () => {
      window.removeEventListener("beforeunload", cb);
    };
  });

  return unloading || (!data && !error && isValidating) ? null : !!error;
};
