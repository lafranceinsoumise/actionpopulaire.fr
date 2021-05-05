import React, { useMemo } from "react";

import Logo from "./Logo";
import MenuLink from "./MenuLink";
import { routeConfig } from "../../app/routes.config";

export const TopBarMainLink = (props) => {
  const { isMobileApp, path } = props;

  const currentRoute = useMemo(() => {
    return Object.values(routeConfig).find((route) => route.match(path));
  }, [path]);

  if (!isMobileApp || !currentRoute) {
    return null;
  }

  return (
    <MenuLink href={currentRoute.getLink()} small>
      {currentRoute.id === "events" ? <Logo /> : <h1>{currentRoute.label}</h1>}
    </MenuLink>
  );
};
