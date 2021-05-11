import React, { useMemo } from "react";

import Logo from "./Logo";
import MenuLink from "./MenuLink";
import { routeConfig } from "../../app/routes.config";
import { getIsConnected } from "@agir/front/globalContext/reducers";
import { useSelector } from "@agir/front/globalContext/GlobalContext";

export const TopBarMainLink = (props) => {
  const { path } = props;
  const isConnected = useSelector(getIsConnected);

  const currentRoute = useMemo(() => {
    return Object.values(routeConfig).find((route) => route.match(path));
  }, [path]);

  if (!isConnected || !currentRoute || currentRoute.id === "events") {
    return <Logo />;
  }

  return <h1>{currentRoute.label}</h1>;
};
