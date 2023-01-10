import React, { useEffect } from "react";
import { Redirect, useLocation } from "react-router-dom";
import useSWRImmutable from "swr/immutable";

import { logout } from "@agir/front/authentication/api";
import { routeConfig } from "@agir/front/app/routes.config";

const Logout = () => {
  const location = useLocation();
  const { data, mutate, isLoading } = useSWRImmutable("/api/session/");

  const isAuthenticated = !isLoading && !!data?.user?.id;

  useEffect(() => {
    if (!isAuthenticated) {
      return;
    }
    mutate(logout, {
      populateCache: (_, data) => ({
        ...data,
        user: false,
        authentication: 0,
      }),
      revalidate: false,
    });
  }, [isAuthenticated, mutate]);

  return data?.user === false ? (
    <Redirect
      to={{
        pathname: routeConfig.login.getLink(),
        state: { ...(location.state || {}) },
      }}
    />
  ) : null;
};

export default Logout;
