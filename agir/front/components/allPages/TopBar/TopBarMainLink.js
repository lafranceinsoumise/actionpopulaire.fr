import React, { useMemo } from "react";

import Logo from "./Logo";
import MenuLink from "./MenuLink";
import { routeConfig } from "../../app/routes.config";
import { useLocation } from "react-router-dom";

export const TopBarMainLink = (props) => {
  const { isMobileApp, path } = props;

  const currentRoute = useMemo(() => {
    let route = Object.values(routeConfig).find((route) => route.match(path));

    // for some pages routeConfig doesn't work, we use useLocation hook instead
    if (typeof route !== "undefined") return route;
    else
      return Object.values(routeConfig).find((route) =>
        route.match(useLocation().pathname)
      );
  }, [path]);

  //console.log(Object.values(routeConfig).find((route) => route.match(path)));
  if (!isMobileApp || !currentRoute) {
    return null;
  }

  return (
    <MenuLink href={currentRoute.getLink()}>
      {currentRoute.id === "events" ? <Logo /> : <h1>{currentRoute.label}</h1>}
    </MenuLink>
  );
};
