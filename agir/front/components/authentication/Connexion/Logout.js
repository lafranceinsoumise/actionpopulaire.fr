import React, { useCallback, useEffect, useState } from "react";
import { Redirect } from "react-router-dom";
import useSWR from "swr";

import { logout } from "@agir/front/authentication/api";
import { routeConfig } from "@agir/front/app/routes.config";

import {
  useSelector,
  useDispatch,
} from "@agir/front/globalContext/GlobalContext";
import {
  getUser,
  getIsSessionLoaded,
} from "@agir/front/globalContext/reducers";
import { setSessionContext } from "@agir/front/globalContext/actions";

const Logout = () => {
  const dispatch = useDispatch();
  const user = useSelector(getUser);
  const isSessionLoaded = useSelector(getIsSessionLoaded);
  const [isLoading, setIsLoading] = useState(false);

  const { data: session, mutate: mutate } = useSWR("/api/session/");

  const doLogout = useCallback(async () => {
    setIsLoading(true);
    await logout();
    setIsLoading(false);
    mutate();
  }, [mutate]);

  useEffect(() => {
    doLogout();
  }, [doLogout]);

  useEffect(() => {
    dispatch(setSessionContext(session));
  }, [dispatch, session]);

  if (!isLoading && isSessionLoaded && !user) {
    return <Redirect to={routeConfig.login.getLink()} />;
  }

  return null;
};

export default Logout;
