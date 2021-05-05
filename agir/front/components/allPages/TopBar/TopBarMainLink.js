import React, { useMemo } from "react";
import styled from "styled-components";

import Logo from "./Logo";
import { routeConfig } from "../../app/routes.config";
import style from "@agir/front/genericComponents/_variables.scss";

const MenuLink = styled.a`
  ${({ small }) =>
    small &&
    `@media only screen and (max-width: ${style.collapse - 1}px) {
          display: none;
      }`}

`;

export const TopBarMainLink = (props) => {
  const { isMobileApp, path } = props;

  const currentRoute = useMemo(() => {
    return Object.values(routeConfig).find((route) => route.match(path));
  }, [path]);

  if (!isMobileApp || !currentRoute) {
    return null;
  }

  return (
    <MenuLink href={currentRoute.getLink()} small={true}>
      {currentRoute.id === "events" ? <Logo /> : <h1>{currentRoute.label}</h1>}
    </MenuLink>
  );
};
