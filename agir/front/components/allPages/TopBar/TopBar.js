import React from "react";
import styled from "styled-components";
import PropTypes from "prop-types";

import { useSelector } from "@agir/front/globalContext/GlobalContext";
import {
  getRoutes,
  getUser,
  getIsSessionLoaded,
  getBackLink,
  getTopBarRightLink,
  getAdminLink,
} from "@agir/front/globalContext/reducers";

import style from "@agir/front/genericComponents/_variables.scss";

import FeatherIcon from "@agir/front/genericComponents/FeatherIcon";
import PageFadeIn from "@agir/front/genericComponents/PageFadeIn";

import Logo from "./Logo";
import RightLink from "./RightLink";
import SearchBar from "./SearchBar";
import AdminLink from "./AdminLink";
import { TopBarMainLink } from "./TopBarMainLink";
import { useMobileApp } from "@agir/front/app/hooks";

const TopBarBar = styled.div`
  position: fixed;
  top: 0;
  left: 0;

  z-index: ${style.zindexTopBar};

  width: 100%;
  padding: 0.75rem 2rem;

  background-color: #fff;
  box-shadow: 0px 0px 3px rgba(0, 35, 44, 0.1),
    0px 3px 2px rgba(0, 35, 44, 0.05);

  @media (max-width: ${+style.collapse - 1}px) {
    padding: 1rem 1.5rem;
  }
`;

const TopBarContainer = styled.div`
  display: flex;
  flex-direction: row;
  justify-content: space-between;

  max-width: 1320px;
  margin: 0 auto;

  h1 {
    font-family: ${style.fontFamilyBase};
    font-style: normal;
    font-weight: 600;
    font-size: 16px;
    line-height: 24px;
  }

  h1:hover {
    text-decoration: none;
  }
`;

const HorizontalFlex = styled.div`
  display: flex;
  align-items: center;
  flex-grow: 1;

  ${({ center }) =>
    center &&
    `
    @media only screen and (max-width: ${style.collapse - 1}px) {
      justify-content: center;
    }
  `}

  & > * {
    margin-left: 1.25em;
    text-align: left;
`;

const MenuLink = styled.div`
  ${({ small }) =>
    small &&
    `@media only screen and (max-width: ${style.collapse - 1}px) {
          display: none;
      }`}

  ${({ large }) =>
    large &&
    `@media only screen and (min-width: ${style.collapse}px) {
          display: none;
      }`}
`;

export const TopBar = ({ path }) => {
  const routes = useSelector(getRoutes);
  const user = useSelector(getUser);
  const isSessionLoaded = useSelector(getIsSessionLoaded);
  const backLink = useSelector(getBackLink);
  const topBarRightLink = useSelector(getTopBarRightLink);
  const adminLink = useSelector(getAdminLink);
  const { isMobileApp } = useMobileApp();

  return (
    <TopBarBar>
      <AdminLink link={adminLink} />
      <TopBarContainer>
        {isSessionLoaded ? (
          backLink ? (
            <MenuLink
              to={backLink.to}
              href={backLink.href}
              route={backLink.route}
              title={backLink.label}
              aria-label={backLink.label}
              small
            >
              <FeatherIcon name="arrow-left" />
            </MenuLink>
          ) : (
            <MenuLink href={routes.search} small>
              <FeatherIcon name="search" />
            </MenuLink>
          )
        ) : null}
        <HorizontalFlex center={path === "/"}>
          <TopBarMainLink isMobileApp={isMobileApp} path={path} small={true} />
          <MenuLink href={routes.dashboard} large={true}>
            <Logo />
          </MenuLink>
          <form method="get" action={routes.search}>
            <SearchBar routes={routes} />
          </form>
        </HorizontalFlex>
        <PageFadeIn ready={isSessionLoaded}>
          <HorizontalFlex>
            <MenuLink href={routes.help} small={true}>
              <FeatherIcon name="help-circle" />
              <span>Aide</span>
            </MenuLink>
            <RightLink
              settingsLink={(isSessionLoaded && topBarRightLink) || undefined}
              routes={routes}
              user={user}
            />
          </HorizontalFlex>
        </PageFadeIn>
      </TopBarContainer>
    </TopBarBar>
  );
};

export default TopBar;

TopBar.propTypes = {
  path: PropTypes.string,
};
