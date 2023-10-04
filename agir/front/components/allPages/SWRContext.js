import PropTypes from "prop-types";
import React from "react";
import { SWRConfig } from "swr";

import axios from "@agir/lib/utils/axios";

const fetcher = async (args) => {
  if (!Array.isArray(args)) {
    args = [args];
  }

  const [url, method = "GET"] = args;

  if (
    // Check if a preload link exists for the requested URL
    document.querySelector(`link[rel="preload"][as="fetch"][href="${url}"]`)
  ) {
    const res = await fetch(url, {
      method,
      credentials: "include",
      mode: "no-cors",
    });

    if (!res.ok) {
      const error = new Error("Error: " + res.statusText);
      error.response = res;
      throw error;
    }

    return res.json();
  }
  const res = await axios({ method, url });
  return res.data;
};

const errorRetry = (error, ...rest) => {
  if ([403, 404].includes(error.status)) return;
  SWRConfig.defaultValue.onErrorRetry(error, ...rest);
};

const SWRContext = ({ children }) => (
  <SWRConfig
    value={{
      fetcher,
      onErrorRetry: errorRetry,
    }}
  >
    {children}
  </SWRConfig>
);

SWRContext.propTypes = {
  children: PropTypes.node,
};

export default SWRContext;
