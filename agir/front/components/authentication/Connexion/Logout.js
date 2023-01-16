import React, { useEffect } from "react";
import { Redirect, useLocation } from "react-router-dom";
import useSWRImmutable from "swr/immutable";
import useSWRMutation from "swr/mutation";

import { logout } from "@agir/front/authentication/api";
import { routeConfig } from "@agir/front/app/routes.config";

const logoutAndMutate = async (mutate) => {
  await logout();
  mutate({
    optimisticData: (data) => ({
      ...data,
      user: false,
      authentication: 0,
    }),
  });
};

const Logout = () => {
  const location = useLocation();

  const { data, isLoading } = useSWRImmutable("/api/session/");
  const { trigger } = useSWRMutation("/api/session/");

  const isAuthenticated = !isLoading && !!data?.user?.id;

  useEffect(() => {
    if (!isAuthenticated) {
      return;
    }
    logoutAndMutate(trigger);
  }, [isAuthenticated, trigger]);

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
