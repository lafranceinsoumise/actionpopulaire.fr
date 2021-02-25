import PropTypes from "prop-types";
import React, { useCallback, useState } from "react";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

import Avatar from "@agir/front/genericComponents/Avatar";
import FeatherIcon from "@agir/front/genericComponents/FeatherIcon";

import MenuLink from "./MenuLink";
import UserMenu from "./UserMenu";

const SettingsMenuLink = styled(MenuLink)`
  @media (min-width: ${style.collapse}px) {
    position: absolute;
    padding: 6px 5px;
    bottom: 0;
    right: 0;
    background-color: ${style.black1000};
    color: ${style.black25};
    width: 42px;
    height: 42px;
    display: flex;
    align-items: flex-start;
    justify-content: flex-end;
    transform: translateY(100%);
    clip-path: polygon(0 0, 100% 0, 100% 100%, 0 0);
    transition: all 100ms ease-in-out;
    cursor: pointer;
    opacity: 0.75;

    &:hover,
    &:focus {
      background-color: ${style.black1000};
      color: ${style.white};
      opacity: 1;
    }
  }
`;

const AnonymousLink = ({ routes }) => {
  return (
    <>
      <MenuLink href={routes.login} className="small-only">
        <FeatherIcon name="user" />
      </MenuLink>
      <MenuLink href={routes.login} className="large-only">
        <span>Connexion</span>
      </MenuLink>
      <MenuLink href={routes.join} className="large-only">
        <span>Inscription</span>
      </MenuLink>
    </>
  );
};

const UserLink = ({ user, routes, ...rest }) => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  const openMenu = useCallback(() => setIsMenuOpen(true), []);
  const closeMenu = useCallback(() => setIsMenuOpen(false), []);

  return (
    <MenuLink
      {...rest}
      style={{ position: "relative" }}
      as="button"
      onClick={openMenu}
    >
      <Avatar displayName={user.displayName} image={user.image} />
      <span className="large-only">{user.displayName}</span>
      <UserMenu
        isOpen={isMenuOpen}
        onDismiss={closeMenu}
        user={user}
        routes={routes}
      />
    </MenuLink>
  );
};

const SettingsLink = (props) => {
  const { settingsLink } = props;
  return (
    <>
      <UserLink {...props} className="large-only" />
      <SettingsMenuLink
        to={settingsLink.to}
        href={settingsLink.href}
        route={settingsLink.route}
        title={settingsLink.label}
        aria-label={settingsLink.label}
      >
        <FeatherIcon name="settings" />
      </SettingsMenuLink>
    </>
  );
};

const RightLink = (props) => {
  const { user, settingsLink } = props;
  if (settingsLink) {
    return <SettingsLink {...props} />;
  }
  if (user) {
    return <UserLink {...props} />;
  }
  return <AnonymousLink {...props} />;
};

RightLink.propTypes = AnonymousLink.propTypes = SettingsLink.propTypes = UserLink.propTypes = {
  user: PropTypes.shape({
    image: PropTypes.string,
    displayName: PropTypes.string,
    isInsoumise: PropTypes.bool,
  }),
  routes: PropTypes.objectOf(
    PropTypes.oneOfType([
      PropTypes.string,
      PropTypes.object,
      PropTypes.arrayOf(
        PropTypes.shape({
          id: PropTypes.string,
          label: PropTypes.string,
          href: PropTypes.string,
        })
      ),
    ])
  ),
  settingsLink: PropTypes.shape({
    to: PropTypes.string,
    href: PropTypes.string,
    route: PropTypes.string,
    label: PropTypes.string,
  }),
};

RightLink.defaultProps = {
  user: null,
  routes: {
    dashboard: "#dashboard",
    search: "#search",
    help: "#help",
    personalInformation: "#personalInformation",
    contactConfiguration: "#contactConfiguration",
    join: "#join",
    login: "#login",
  },
  settingsLink: null,
};

export default RightLink;
