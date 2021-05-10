import React from "react";
import styled from "styled-components";
import PropTypes from "prop-types";

import { useIsDesktop } from "@agir/front/genericComponents/grid.js";
import { useSelector } from "@agir/front/globalContext/GlobalContext";
import {
  getRoutes,
  getUser,
  getIsSessionLoaded,
  getBackLink,
  getTopBarRightLink,
  getAdminLink,
} from "@agir/front/globalContext/reducers";
import { Hide } from "@agir/front/genericComponents/grid";

import style from "@agir/front/genericComponents/_variables.scss";

import FeatherIcon from "@agir/front/genericComponents/FeatherIcon";
import PageFadeIn from "@agir/front/genericComponents/PageFadeIn";

import Logo from "./Logo";
import RightLink from "./RightLink";
import SearchBar from "./SearchBar";
import AdminLink from "./AdminLink";
import MenuLink from "./MenuLink";
import { TopBarMainLink } from "./TopBarMainLink";
import DownloadApp from "@agir/front/genericComponents/DownloadApp.js";
import { useMobileApp } from "@agir/front/app/hooks";

const NavBar = styled.div``;

const NavbarContainer = styled.div`
  position: fixed;
  top: 0;
  left: 0;
  z-index: ${style.zindexTopBar};
  width: 100%;
  background-color: #fff;

  ${NavBar} {
    padding: 0.75rem 2rem;
    box-shadow: 0px 0px 3px rgba(0, 35, 44, 0.1),
      0px 3px 2px rgba(0, 35, 44, 0.05);

    @media (max-width: ${+style.collapse - 1}px) {
      padding: 1rem 1.5rem;
    }

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
  justify-content: space-between;
  max-width: 1320px;
  margin: 0 auto;
  flex-grow: 1;

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

  & > * {
    margin-left: 1.25em;
  }

  form {
    flex-grow: inherit;
  }

  ${({ center }) =>
    center &&
    `
    @media only screen and (max-width: ${style.collapse - 1}px) {
      justify-content: center;
    }
  `}
`;

export const TopBar = ({ path }) => {
  const routes = useSelector(getRoutes);
  const user = useSelector(getUser);
  const isSessionLoaded = useSelector(getIsSessionLoaded);
  const backLink = useSelector(getBackLink);
  const topBarRightLink = useSelector(getTopBarRightLink);
  const adminLink = useSelector(getAdminLink);
  const isDesktop = useIsDesktop();
  const { isMobileApp } = useMobileApp();

  return (
    <NavbarContainer>
      {!isDesktop && <DownloadApp />}

      <NavBar>
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
              >
                <FeatherIcon name="arrow-left" />
              </MenuLink>
            ) : (
              <MenuLink href={routes.search}>
                <FeatherIcon name="search" />
              </MenuLink>
            )
          ) : null}
          <HorizontalFlex center={path === "/"}>
            <Hide over>
              <TopBarMainLink isMobileApp={isMobileApp} path={path} />
            </Hide>
            <Hide under>
              <MenuLink href={routes.dashboard}>
                <Logo />
              </MenuLink>
            </Hide>
            <Hide under as="form" method="get" action={routes.search}>
              <SearchBar routes={routes} />
            </Hide>
          </HorizontalFlex>
          <PageFadeIn ready={isSessionLoaded}>
            <HorizontalFlex>
              <Hide under>
                <MenuLink href={routes.help}>
                  <FeatherIcon name="help-circle" />
                  <span>Aide</span>
                </MenuLink>
              </Hide>
              <RightLink
                settingsLink={(isSessionLoaded && topBarRightLink) || undefined}
                routes={routes}
                user={user}
              />
            </HorizontalFlex>
          </PageFadeIn>
        </TopBarContainer>
      </NavBar>
    </NavbarContainer>
  );
};

export default TopBar;

TopBar.propTypes = {
  path: PropTypes.string,
};
