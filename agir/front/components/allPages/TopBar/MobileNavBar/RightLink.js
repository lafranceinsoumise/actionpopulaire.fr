import PropTypes from "prop-types";
import React, { useState } from "react";

import Avatar from "@agir/front/genericComponents/Avatar";
import BottomSheet from "@agir/front/genericComponents/BottomSheet";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";

import { IconLink } from "./StyledBar";
import UserMenu from "../UserMenu";

export const RightLink = (props) => {
  const { user, settingsLink } = props;
  const [isUserMenuOpen, setIsUserMenuOpen] = useState(false);

  if (!user) {
    return (
      <IconLink route="login">
        <RawFeatherIcon name="user" width="1.5rem" height="1.5rem" />
      </IconLink>
    );
  }

  if (settingsLink) {
    return (
      <IconLink
        to={settingsLink.to}
        href={settingsLink.href}
        route={settingsLink.route}
        title={settingsLink.label}
        aria-label={settingsLink.label}
      >
        <RawFeatherIcon name="settings" width="1.5rem" height="1.5rem" />
      </IconLink>
    );
  }

  const openUserMenu = () => setIsUserMenuOpen(true);
  const closeUserMenu = () => setIsUserMenuOpen(false);

  return (
    <>
      <Avatar
        as="button"
        aria-label="Paramètres du compte"
        onClick={openUserMenu}
        displayName={user.displayName}
        image={user.image}
        style={{
          border: "none",
          width: "2rem",
          height: "2rem",
        }}
      />
      <BottomSheet
        isOpen={isUserMenuOpen}
        onDismiss={closeUserMenu}
        shouldDismissOnClick
      >
        <UserMenu user={user} />
      </BottomSheet>
    </>
  );
};

RightLink.propTypes = {
  user: PropTypes.oneOfType([PropTypes.bool, PropTypes.object]),
  settingsLink: PropTypes.object,
};

export default RightLink;
