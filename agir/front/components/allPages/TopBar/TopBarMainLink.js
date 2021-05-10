import React, { useMemo } from "react";

import Logo from "./Logo";
import MenuLink from "./MenuLink";
import { routeConfig } from "../../app/routes.config";

export const TopBarMainLink = (props) => {
  const { path } = props;

  const currentRoute = useMemo(() => {
    return Object.values(routeConfig).find((route) => route.match(path));
  }, [path]);

  if (!currentRoute) {
    return (
      <MenuLink route="events">
        <Logo />
      </MenuLink>
    );
  }

  return (
    <MenuLink route={currentRoute.id}>
      {currentRoute.id === "events" ? <Logo /> : <h1>{currentRoute.label}</h1>}
    </MenuLink>
  );
};
