import PropTypes from "prop-types";
import React, { useCallback, useState } from "react";

import Avatar from "@agir/front/genericComponents/Avatar";
import FeatherIcon from "@agir/front/genericComponents/FeatherIcon";

import MenuLink from "./MenuLink";
import UserMenu from "./UserMenu";

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

  const openMenu = useCallback(() => {
    setIsMenuOpen(true);
  }, []);
  const closeMenu = useCallback(() => {
    setIsMenuOpen(false);
  }, []);

  return (
    <div style={{ position: "relative", padding: 0 }}>
      <MenuLink {...rest} style={{ padding: 0 }} as="button" onClick={openMenu}>
        <Avatar displayName={user.displayName} image={user.image} />
        <span className="large-only">{user.displayName}</span>
      </MenuLink>
      <UserMenu
        isOpen={isMenuOpen}
        onDismiss={closeMenu}
        user={user}
        routes={routes}
      />
    </div>
  );
};

const SettingsLink = (props) => {
  const { settingsLink } = props;
  return (
    <>
      <MenuLink
        to={settingsLink.to}
        href={settingsLink.href}
        route={settingsLink.route}
        className="small-only"
        title={settingsLink.label}
        aria-label={settingsLink.label}
      >
        <FeatherIcon name="settings" />
      </MenuLink>
      <UserLink {...props} className="large-only" />
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
