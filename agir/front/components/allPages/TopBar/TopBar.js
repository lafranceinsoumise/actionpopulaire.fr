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
import { useMobileApp } from "@agir/front/app/hooks";
import { routeConfig } from "@agir/front/app/routes.config";

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
    justify-content: center;
  `}

  & > * {
    margin-left: 1.25em;
    text-align: left;
  }
`;

const MenuLink = styled.a`
  "@media only screen and 
  (${(small) => small ? "min-width: ${style.collapse}" : "max-width: ${style.collapse - 1}"}px) {
      display-none;
   }
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
          {(() => {
            if (isMobileApp) {
              for (const route of Object.entries(routeConfig)) {
                if (path === "/") {
                  return (
                    <MenuLink href={routes.dashboard} small>
                      <Logo />
                    </MenuLink>
                  );
                } else if (route[1].path === path) {
                  return (
                    <MenuLink href={route[1].path} small>
                      <h1>{route[1].label}</h1>
                    </MenuLink>
                  );
                } else if (Array.isArray(route[1].path)) {
                  // if route have multiple paths in an array
                  for (const element of route[1].path) {
                    if (element === path)
                      return (
                        <MenuLink href={element} small>
                          <h1>{route[1].label}</h1>
                        </MenuLink>
                      );
                  }
                }
              }
            }
          })()}
          <MenuLink href={routes.dashboard}>
            <Logo />
          </MenuLink>
          <form method="get" action={routes.search}>
            <SearchBar routes={routes} />
          </form>
        </HorizontalFlex>
        <PageFadeIn ready={isSessionLoaded}>
          <HorizontalFlex>
            <MenuLink href={routes.help}>
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
