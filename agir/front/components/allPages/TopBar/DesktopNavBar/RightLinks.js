import PropTypes from "prop-types";
import React, { useState } from "react";
import styled from "styled-components";

import Avatar from "@agir/front/genericComponents/Avatar";
import FeatherIcon from "@agir/front/genericComponents/FeatherIcon";
import Link from "@agir/front/app/Link";
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
    color: ${(props) => props.theme.black1000};
  }
`;

const IconLink = styled(Link)`
  cursor: pointer;
  background-color: transparent;
  border: none;
  display: inline-flex;
  height: 100%;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 0 11px;
  font-size: 0.75rem;
  position: relative;
  color: ${(props) =>
    props.$active ? (props) => props.theme.primary500 : props.theme.black1000};
  box-shadow: ${(props) =>
    props.$active
      ? `0px -2px ${props.theme.primary500} inset`
      : `0px 0px ${props.theme.primary500}`};
  transition: color, box-shadow 200ms ease-in-out;

  &:hover {
    color: ${(props) => props.theme.primary500};
    text-decoration: none;
  }

  &:last-child {
    padding-right: 0;
  }

  span {
    margin: 0;
    margin-top: 5px;
    max-width: 75px;
    text-overflow: ellipsis;
    overflow: hidden;
    word-wrap: initial;
    white-space: nowrap;
  }

  small {
    display: flex;
    color: ${(props) => props.theme.white};
    position: absolute;
    background-color: ${(props) => props.theme.redNSP};
    font-weight: 700;
    font-size: 11px;
    border-radius: 100%;
    align-items: center;
    justify-content: center;
    top: 10px;
    right: 20px;
    width: 18px;
    height: 18px;
    overflow: hidden;
    white-space: nowrap;

    &:empty {
      top: 12px;
      right: 30px;
      width: 0.5rem;
      height: 0.5rem;
    }
  }
`;
const StyledWrapper = styled.div`
  height: 100%;
  display: flex;
  margin-left: auto;
  align-items: center;
`;

const RightLinks = (props) => {
  const { user, path, unreadActivityCount, unreadMessageCount } = props;

  const [isUserMenuOpen, setIsUserMenuOpen] = useState(false);

  if (!user) {
    return (
      <StyledWrapper>
        <StyledLink route="help">Aide</StyledLink>
        <Spacer size="1.5rem" />
        <StyledLink route="login">Connexion</StyledLink>
        <Spacer size="1.5rem" />
        <StyledLink route="signup">Inscription</StyledLink>
      </StyledWrapper>
    );
  }

  const openUserMenu = () => setIsUserMenuOpen(true);
  const closeUserMenu = () => setIsUserMenuOpen(false);

  return (
    <StyledWrapper style={{ position: "relative" }}>
      <Popin
        isOpen={isUserMenuOpen}
        onDismiss={closeUserMenu}
        shouldDismissOnClick
        position="bottom-right"
      >
        <UserMenu user={user} />
      </Popin>
      <IconLink route="events" $active={routeConfig.events.match(path)}>
        <FeatherIcon name="home" />
        <span>Accueil</span>
      </IconLink>
      <IconLink route="activities" $active={routeConfig.activities.match(path)}>
        <FeatherIcon name="bell" />
        <span>Notifications</span>
        {unreadActivityCount > 0 && (
          <small style={{ right: 30 }}>
            {Math.min(unreadActivityCount, 99)}
          </small>
        )}
      </IconLink>
      <IconLink route="messages" $active={routeConfig.messages.match(path)}>
        <FeatherIcon name="mail" />
        <span>Messages</span>
        {unreadMessageCount > 0 && (
          <small>{Math.min(unreadMessageCount, 99)}</small>
        )}
      </IconLink>
      <IconLink route="tools" $active={routeConfig.tools.match(path)}>
        <FeatherIcon name="flag" />
        <span>Outils</span>
      </IconLink>
      <IconLink as="button" onClick={openUserMenu}>
        <Avatar
          displayName={user.displayName}
          image={user.image}
          style={{ width: "28px", height: "28px", marginTop: 0 }}
        />
        <span>{user.displayName}</span>
      </IconLink>
    </StyledWrapper>
  );
};

RightLinks.propTypes = {
  user: PropTypes.oneOfType([
    PropTypes.shape({
      displayName: PropTypes.string,
      image: PropTypes.image,
    }),
    PropTypes.bool,
  ]),
  path: PropTypes.string,
  unreadMessageCount: PropTypes.number,
  unreadActivityCount: PropTypes.number,
};
export default RightLinks;
