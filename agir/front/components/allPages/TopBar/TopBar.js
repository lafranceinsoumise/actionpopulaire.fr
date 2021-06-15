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
import { useUnreadActivityCount } from "@agir/activity/common/hooks";
import { useSelector } from "@agir/front/globalContext/GlobalContext";
import { routeConfig } from "@agir/front/app/routes.config";
import { useUnreadMessageCount } from "@agir/msgs/hooks";
import { Hide } from "@agir/front/genericComponents/grid.js";
import style from "@agir/front/genericComponents/_variables.scss";

import FeatherIcon from "@agir/front/genericComponents/FeatherIcon";
import PageFadeIn from "@agir/front/genericComponents/PageFadeIn";
import DownloadApp from "@agir/front/genericComponents/DownloadApp";
import Button from "@agir/front/genericComponents/Button";

import Logo from "./Logo";
import RightLink, { AnonymousLinks } from "./RightLink";
import SearchBar from "./SearchBar";
import AdminLink from "./AdminLink";
import MenuLink, { TopbarLink } from "./MenuLink";
import { TopBarMainLink } from "./TopBarMainLink";

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
    background-color: #fff;
    box-shadow: 0px 0px 3px rgba(0, 35, 44, 0.1),
      0px 3px 2px rgba(0, 35, 44, 0.05);

    @media (max-width: ${style.collapse}px) {
      padding: 1rem 1.5rem;
      height: 100%;
    }
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

  @media only screen and (max-width: ${style.collapse}px) {
    justify-content: ${({ center }) => (center ? "center" : "flex-start")};
  }

  & > * {
    margin-left: 1.25em;
  }

  form {
    flex-grow: inherit;
  }
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
  const isConnected = useSelector(getIsConnected);

  const unreadMessageCount = useUnreadMessageCount();
  const unreadActivityCount = useUnreadActivityCount();

  return (
    <NavbarContainer>
      {!hideBannerDownload && <DownloadApp />}
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
                <MenuLink as={"a"} href={routeConfig.events.getLink()}>
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
                      <MenuLink route="events">
                        <TopbarLink $active={routeConfig.events.match(path)}>
                          <FeatherIcon name="home" />
                          <span>Accueil</span>
                          <div />
                        </TopbarLink>
                      </MenuLink>
                      <MenuLink route="activities">
                        <TopbarLink
                          $active={routeConfig.activities.match(path)}
                        >
                          <FeatherIcon name="bell" />
                          <span>Notifications</span>
                          <div />
                          {unreadActivityCount > 0 && (
                            <small style={{ right: 30 }}>
                              {Math.min(unreadActivityCount, 99)}
                            </small>
                          )}
                        </TopbarLink>
                      </MenuLink>
                      <MenuLink route="messages">
                        <TopbarLink $active={routeConfig.messages.match(path)}>
                          <FeatherIcon name="mail" />
                          <span>Messages</span>
                          <div />
                          {unreadMessageCount > 0 && (
                            <small>{Math.min(unreadMessageCount, 99)}</small>
                          )}
                        </TopbarLink>
                      </MenuLink>
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
  hideBannerDownload: PropTypes.bool,
};
