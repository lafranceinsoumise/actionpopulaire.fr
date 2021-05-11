import React, { useMemo } from "react";

import Logo from "./Logo";
import { routeConfig } from "../../app/routes.config";
import { getIsConnected } from "@agir/front/globalContext/reducers";
import { useSelector } from "@agir/front/globalContext/GlobalContext";
import PropTypes from "prop-types";
import MenuLink from "@agir/front/allPages/TopBar/MenuLink";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

const TopBarMainLabel = styled.h1`
  font-family: ${style.fontFamilyBase};
  font-style: normal;
  font-weight: 600;
  font-size: 16px;
  line-height: 24px;
  margin: 1px 0 -1px 0;

  &:hover {
    text-decoration: none;
  }
`;

export const TopBarMainLink = (props) => {
  const { path } = props;
  const isConnected = useSelector(getIsConnected);

  const currentRoute = useMemo(() => {
    return Object.values(routeConfig).find((route) => route.match(path));
  }, [path]);

  if (!isConnected || !currentRoute || currentRoute.id === "events") {
    return (
      <MenuLink as={"a"} href="/">
        <Logo />
      </MenuLink>
    );
  }

  return <TopBarMainLabel>{currentRoute.label}</TopBarMainLabel>;
};

TopBarMainLink.propTypes = {
  path: PropTypes.string,
};
