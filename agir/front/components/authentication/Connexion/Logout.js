import React, { useCallback, useEffect } from "react";
import { Redirect, useLocation } from "react-router-dom";
import useSWR from "swr";

import { logout } from "@agir/front/authentication/api";
import { routeConfig } from "@agir/front/app/routes.config";

const Logout = () => {
  const location = useLocation();
  const {
    data: session,
    mutate: mutate,
    isValidating,
  } = useSWR("/api/session/", {
    revalidateIfStale: false,
    revalidateOnFocus: false,
    revalidateOnReconnect: false,
  });
  const isAuthenticated = !isValidating && !!session?.user?.id;
  useEffect(() => {
    if (!isAuthenticated) {
      return;
    }
    const doLogout = async () => {
      await logout();
      mutate(
        (session) => ({ ...session, user: false, authentication: 0 }),
        false
      );
    };
    doLogout();
  }, [isAuthenticated]);
  return session?.user === false ? (
    <Redirect
      to={{
        pathname: routeConfig.login.getLink(),
        state: { ...(location.state || {}) },
      }}
    />
  ) : null;
};

export default Logout;
