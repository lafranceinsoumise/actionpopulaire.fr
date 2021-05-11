import PropTypes from "prop-types";
import React, { useCallback, useState } from "react";

import Avatar from "@agir/front/genericComponents/Avatar";
import FeatherIcon from "@agir/front/genericComponents/FeatherIcon";
import { Hide } from "@agir/front/genericComponents/grid";

import MenuLink from "./MenuLink";
import UserMenu from "./UserMenu";

const AnonymousLink = () => {
  return (
    <>
      <Hide over>
        <MenuLink route="login">
          <FeatherIcon name="user" />
        </MenuLink>
      </Hide>
      <Hide under>
        <MenuLink route="login">
          <span>Connexion</span>
        </MenuLink>
      </Hide>
      <Hide under as={"MenuLink"}>
        <MenuLink route="signup">
          <span>Inscription</span>
        </MenuLink>
      </Hide>
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
        <Hide under>
          <span>{user.displayName}</span>
        </Hide>
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
      <Hide under>
        <UserLink {...props} />
      </Hide>

      <Hide over>
        <MenuLink
          to={settingsLink.to}
          href={settingsLink.href}
          route={settingsLink.route}
          title={settingsLink.label}
          aria-label={settingsLink.label}
        >
          <FeatherIcon name="settings" />
        </MenuLink>
      </Hide>
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
  user: PropTypes.oneOfType([
    PropTypes.shape({
      image: PropTypes.string,
      displayName: PropTypes.string,
      isInsoumise: PropTypes.bool,
    }),
    PropTypes.bool,
  ]),
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
