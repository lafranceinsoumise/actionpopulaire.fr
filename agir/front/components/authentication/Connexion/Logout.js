import React, { useCallback, useMemo } from "react";
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
  } = useSWR("/api/session/");

  const doLogout = useCallback(async () => {
    await logout();
    mutate(
      (session) => ({
        ...session,
        user: false,
        authentication: 0,
      }),
      false
    );
  }, [mutate]);

  useMemo(() => {
    !isValidating && doLogout();
  }, [isValidating, doLogout]);

  if (session && !session.user) {
    return (
      <Redirect
        to={{
          pathname: routeConfig.login.getLink(),
          state: { ...(location.state || {}) },
        }}
      />
    );
  }

  return null;
};

export default Logout;
