import React from "react";
import styled from "styled-components";
import { useLocation } from "react-router-dom";

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

import MenuLink from "./MenuLink";
import Logo from "./Logo";
import RightLink from "./RightLink";
import SearchBar from "./SearchBar";
import AdminLink from "./AdminLink";
import { useMobileApp } from "@agir/front/app/hooks";
import routes, { routeConfig, BASE_PATH } from "@agir/front/app/routes.config";

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

  & .large-only {
    @media only screen and (max-width: ${+style.collapse - 1}px) {
      display: none;
    }
  }

  & .small-only {
    @media only screen and (min-width: ${style.collapse}px) {
      display: none;
    }
  }

  .grow {
    flex-grow: 1;
  }

  .justify {
    justify-content: left;
  }

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

  & > * {
    margin-left: 1.25em;
    text-align: left;
  }
`;

export const TopBar = () => {
  const routes = useSelector(getRoutes);
  const user = useSelector(getUser);
  const isSessionLoaded = useSelector(getIsSessionLoaded);
  const backLink = useSelector(getBackLink);
  const topBarRightLink = useSelector(getTopBarRightLink);
  const adminLink = useSelector(getAdminLink);
  const { pathname } = useLocation();
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
              className="small-only"
              title={backLink.label}
              aria-label={backLink.label}
            >
              <FeatherIcon name="arrow-left" />
            </MenuLink>
          ) : (
            <MenuLink href={routes.search} className="small-only">
              <FeatherIcon name="search" />
            </MenuLink>
          )
        ) : null}
        <HorizontalFlex className="grow justify">
          {(() => {
            if (isMobileApp) {
              for (const route of Object.entries(routeConfig)) {
                // we want the logo only on the main page
                if (pathname === "/")
                  return (
                    <MenuLink href={routes.dashboard} className="small-only">
                      <Logo />
                    </MenuLink>
                  );
                if (route[1].path === pathname) {
                  return (
                    <MenuLink href={route[1].path} className="small-only">
                      <h1>{route[1].label}</h1>
                    </MenuLink>
                  );
                } else if (Array.isArray(route[1].path)) {
                  // if route have multiple paths in an array
                  for (const element of route[1].path) {
                    if (element === pathname)
                      return (
                        <MenuLink href={element} className="small-only">
                          <h1>{route[1].label}</h1>
                        </MenuLink>
                      );
                  }
                }
              }
            }
          })()}
          <MenuLink href={routes.dashboard} className="large-only">
            <Logo />
          </MenuLink>
          <form className="large-only grow" method="get" action={routes.search}>
            <SearchBar routes={routes} />
          </form>
        </HorizontalFlex>
        <PageFadeIn ready={isSessionLoaded}>
          <HorizontalFlex>
            <MenuLink href={routes.help} className="large-only">
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
