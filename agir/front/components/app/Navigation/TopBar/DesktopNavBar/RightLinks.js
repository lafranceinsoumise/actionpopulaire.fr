import PropTypes from "prop-types";
import React, { useRef, useState } from "react";
import styled from "styled-components";

import Avatar from "@agir/front/genericComponents/Avatar";
import CounterBadge from "@agir/front/app/Navigation/CounterBadge";
import FeatherIcon from "@agir/front/genericComponents/FeatherIcon";
import Link from "@agir/front/app/Link";
import PageFadeIn from "@agir/front/genericComponents/PageFadeIn";
import Popin from "@agir/front/genericComponents/Popin";
import Spacer from "@agir/front/genericComponents/Spacer";

import UserMenu from "../UserMenu";

import { routeConfig } from "@agir/front/app/routes.config";

const StyledLink = styled(Link)`
  display: inline-flex;
  height: 100%;
  align-items: center;
  font-weight: 400;
  height: 3rem;
  border: none;
  background-color: transparent;
  cursor: pointer;

  &,
  &:hover,
  &:focus {
    color: ${(props) => props.theme.text1000};
  }
`;

const IconLink = styled(Link)`
  cursor: pointer;
  background-color: transparent;
  border: none;
  display: inline-flex;
  height: 100%;
  min-width: 60px;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 0 11px;
  font-size: 0.75rem;
  color: ${(props) =>
    props.$active ? (props) => props.theme.primary500 : props.theme.text1000};
  box-shadow: ${(props) =>
    props.$active
      ? `0px -2px ${props.theme.primary500} inset`
      : `0px 0px ${props.theme.primary500}`};
  transition:
    color,
    box-shadow 200ms ease-in-out;

  &:hover {
    color: ${(props) => props.theme.primary500};
    text-decoration: none;
  }

  &:last-child {
    padding-right: 0;
  }

  & > * {
    margin: 5px 0 0 0;
    max-width: 75px;
    text-overflow: ellipsis;
    overflow: hidden;
    word-wrap: initial;
    white-space: nowrap;

    &:first-child {
      height: 28px;
    }
  }
`;

const CounterIconLink = styled(IconLink)`
  & > i {
    font-style: normal;
    display: inline-grid;
    grid-template-columns: 9px 15px 9px 9px;
    grid-template-rows: 100%;

    & > * {
      grid-column: 2/4;
      grid-row: 1/2;
    }

    ${CounterBadge} {
      grid-column: 3/5;
      height: 1.125rem;
      width: 1.125rem;
    }
  }
`;

const TabletIconLink = styled(IconLink)`
  display: none;

  @media (max-width: ${(props) => props.theme.collapseTablet}px) {
    display: inline-flex;
  }
`;

const StyledWrapper = styled(PageFadeIn)`
  height: 100%;
  display: flex;
  margin-left: auto;
  align-items: center;
`;

const RightLinks = (props) => {
  const {
    isLoading,
    hasLayout,
    user,
    path,
    unreadActivityCount,
    unreadMessageCount,
  } = props;

  const userMenuLink = useRef();
  const [isUserMenuOpen, setIsUserMenuOpen] = useState(false);

  const openUserMenu = () => setIsUserMenuOpen(true);
  const closeUserMenu = () => {
    setIsUserMenuOpen(false);
    userMenuLink.current.focus();
  };

  return (
    <StyledWrapper ready={!isLoading} style={{ position: "relative" }}>
      {!user ? (
        <>
          <StyledLink route="help">Aide</StyledLink>
          <Spacer size="1.5rem" />
          <StyledLink route="login">Connexion</StyledLink>
          <Spacer size="1.5rem" />
          <StyledLink route="signup">Inscription</StyledLink>
        </>
      ) : (
        <>
          <Popin
            isOpen={isUserMenuOpen}
            onDismiss={closeUserMenu}
            shouldDismissOnClick={false}
            position="bottom-right"
          >
            <UserMenu user={user} />
          </Popin>
          <IconLink route="events" $active={routeConfig.events.match(path)}>
            <FeatherIcon name="home" />
            <span>Accueil</span>
          </IconLink>
          <IconLink
            route="actionTools"
            $active={routeConfig.actionTools.match(path)}
          >
            <FeatherIcon name="flag" />
            <span>Agir</span>
          </IconLink>
          <IconLink route="groups" $active={routeConfig.groups.match(path)}>
            <FeatherIcon name="users" />
            <span>Groupes</span>
          </IconLink>
          <CounterIconLink
            route="activities"
            $active={routeConfig.activities.match(path)}
          >
            <i>
              <FeatherIcon name="bell" />
              <CounterBadge value={unreadActivityCount} />
            </i>
            <span>Notifications</span>
          </CounterIconLink>
          <CounterIconLink
            route="messages"
            $active={routeConfig.messages.match(path)}
          >
            <i>
              <FeatherIcon name="mail" />
              <CounterBadge value={unreadMessageCount} />
            </i>
            <span>Messages</span>
          </CounterIconLink>
          <IconLink as="button" onClick={openUserMenu} ref={userMenuLink}>
            <Avatar
              displayName={user.displayName}
              image={user.image}
              style={{ width: "28px", height: "28px" }}
            />
            <span>{user.displayName}</span>
          </IconLink>
        </>
      )}
    </StyledWrapper>
  );
};

RightLinks.propTypes = {
  isLoading: PropTypes.bool,
  user: PropTypes.oneOfType([PropTypes.object, PropTypes.bool]),
  path: PropTypes.string,
  unreadMessageCount: PropTypes.number,
  unreadActivityCount: PropTypes.number,
  hasLayout: PropTypes.bool,
};
export default RightLinks;
