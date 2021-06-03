import React from "react";
import styled from "styled-components";
import PropTypes from "prop-types";

import {
  getAdminLink,
  getBackLink,
  getIsConnected,
  getIsSessionLoaded,
  getRoutes,
  getTopBarRightLink,
  getUser,
} from "@agir/front/globalContext/reducers";
import { useHasUnreadActivity } from "@agir/activity/common/hooks";
import { useSelector } from "@agir/front/globalContext/GlobalContext";

import { useIsDesktop, Hide } from "@agir/front/genericComponents/grid.js";
import style from "@agir/front/genericComponents/_variables.scss";

import FeatherIcon from "@agir/front/genericComponents/FeatherIcon";
import PageFadeIn from "@agir/front/genericComponents/PageFadeIn";
import DownloadApp from "@agir/front/genericComponents/DownloadApp.js";
import Button from "@agir/front/genericComponents/Button";
import Logo from "./Logo";
import RightLink, { AnonymousLinks } from "./RightLink";
import SearchBar from "./SearchBar";
import AdminLink from "./AdminLink";
import MenuLink, { TopbarLink } from "./MenuLink";
import { TopBarMainLink } from "./TopBarMainLink";
import { routeConfig } from "@agir/front/app/routes.config";

const NavBar = styled.div``;

const NavbarContainer = styled.div`
  position: fixed;
  top: 0;
  left: 0;
  z-index: ${style.zindexTopBar};
  width: 100%;
  background-color: #fff;

  ${NavBar} {
  height: 72px;
  align-items: center;
  display: flex;
  box-shadow: 0px 0px 3px rgba(0, 35, 44, 0.1),
    0px 3px 2px rgba(0, 35, 44, 0.05);

  @media (max-width: ${style.collapse}px) {
    padding: 1rem 1.5rem;
  }

  background-color: #fff;
  box-shadow: 0px 0px 3px rgba(0, 35, 44, 0.1),
    0px 3px 2px rgba(0, 35, 44, 0.05);
  @media (max-width: ${style.collapse}px) {
    padding: 1rem 1.5rem;
    height: 100%;
  }
`;

const TopBarContainer = styled.div`
  display: flex;
  justify-content: space-between;
  max-width: 1320px;
  margin: 0 auto;
  flex-grow: 1;
  height: 100%;
  align-items: center;
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

const StyledButton = styled(Button)`
  height: 40px;
  font-size: 16px;
  font-weight: 500;
  border-radius: 0.5rem;
`;

export const TopBar = (props) => {
  const { path, hideBannerDownload } = props;
  const routes = useSelector(getRoutes);
  const user = useSelector(getUser);
  const isSessionLoaded = useSelector(getIsSessionLoaded);
  const backLink = useSelector(getBackLink);
  const topBarRightLink = useSelector(getTopBarRightLink);
  const adminLink = useSelector(getAdminLink);
  const isDesktop = useIsDesktop();
  const isConnected = useSelector(getIsConnected);

  const hasUnreadActivity = useHasUnreadActivity();

  return (
    <NavbarContainer>
      {!isDesktop && !hideBannerDownload && <DownloadApp />}
      <NavBar>
        <AdminLink link={adminLink} />
        <TopBarContainer>
          {isSessionLoaded ? (
            backLink ? (
              <Hide over>
                <MenuLink
                  to={backLink.to}
                  href={backLink.href}
                  route={backLink.route}
                  title={backLink.label}
                  aria-label={backLink.label}
                >
                  <FeatherIcon name="arrow-left" />
                </MenuLink>
              </Hide>
            ) : (
              <Hide over>
                <MenuLink href={routes.search}>
                  <FeatherIcon name="search" />
                </MenuLink>
              </Hide>
            )
          ) : null}
          <HorizontalFlex
            center={!isConnected || path === "/" || typeof path === "undefined"}
          >
            <Hide over>
              <TopBarMainLink path={path} />
            </Hide>
            <Hide under>
              <div style={{ display: "flex", alignItems: "center" }}>
                <MenuLink as={"a"} href="/">
                  <Logo />
                </MenuLink>
                {isConnected && (
                  <StyledButton
                    small
                    as="Link"
                    color="secondary"
                    route="createEvent"
                    icon="plus"
                  >
                    Créer un événement
                  </StyledButton>
                )}
              </div>
            </Hide>
            <Hide under as="form" method="get" action={routes.search}>
              <SearchBar isConnected={isConnected} />
            </Hide>
          </HorizontalFlex>

          <PageFadeIn ready={isSessionLoaded}>
            <HorizontalFlex>
              {!isConnected ? (
                <>
                  <Hide under>
                    <MenuLink href={routes.help}>
                      <span>Aide</span>
                    </MenuLink>
                  </Hide>
                  <AnonymousLinks />
                </>
              ) : (
                <>
                  <Hide under>
                    <div style={{ display: "flex" }}>
                      <MenuLink route="events" href="/">
                        <TopbarLink $active={"/" === path}>
                          <FeatherIcon name="home" />
                          <span>Accueil</span>
                          <div />
                        </TopbarLink>
                      </MenuLink>
                      <MenuLink route="activities" href="/activite/">
                        <TopbarLink
                          isBadge={hasUnreadActivity}
                          $active={"/activite/" === path}
                        >
                          <FeatherIcon name="bell" />
                          <span>Notifications</span>
                          <div />
                          <div class="notif" />
                        </TopbarLink>
                      </MenuLink>
                      {false && (
                        <MenuLink href="#">
                          <TopbarLink>
                            <FeatherIcon name="mail" />
                            <span>Messages</span>
                            <div />
                          </TopbarLink>
                        </MenuLink>
                      )}
                      <MenuLink href={routes.help}>
                        <TopbarLink>
                          <FeatherIcon name="help-circle" />
                          <span>Aide</span>
                          <div />
                        </TopbarLink>
                      </MenuLink>
                    </div>
                  </Hide>
                  <RightLink
                    settingsLink={
                      (isSessionLoaded && topBarRightLink) || undefined
                    }
                    routes={routes}
                    user={user}
                  />
                </>
              )}
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
