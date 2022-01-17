import PropTypes from "prop-types";
import React, { useState } from "react";

import Avatar from "@agir/front/genericComponents/Avatar";
import BottomSheet from "@agir/front/genericComponents/BottomSheet";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";
import Spacer from "@agir/front/genericComponents/Spacer";
import ButtonMuteMessage from "@agir/front/genericComponents/ButtonMuteMessage";

import { MessageOptions } from "@agir/msgs/MessagePage/MessageThreadMenu.js";
import { IconLink } from "./StyledBar";
import UserMenu from "../UserMenu";
import { routeConfig } from "@agir/front/app/routes.config";

export const RightLink = (props) => {
  const { isLoading, user, settingsLink } = props;
  const [isUserMenuOpen, setIsUserMenuOpen] = useState(false);

  let pathname = window.location.pathname;
  const matchMessagesPage = pathname === "/messages/";
  const matchMessagePage =
    routeConfig.messages.match(pathname) && !matchMessagesPage;
  pathname = pathname.slice(0, pathname.length - 1);
  const messagePk = matchMessagePage
    ? pathname.slice(pathname.lastIndexOf("/") + 1)
    : undefined;

  if (isLoading) {
    return <IconLink as={Spacer} size="32px" />;
  }

  if (!user) {
    return (
      <IconLink route="login">
        <RawFeatherIcon name="user" width="24px" height="24px" />
      </IconLink>
    );
  }

  if (matchMessagesPage) {
    return <MessageOptions />;
  }

  // Show muted message settings
  if (matchMessagePage) {
    return <ButtonMuteMessage message={{ id: messagePk }} />;
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
        <RawFeatherIcon name="settings" width="24px" height="24px" />
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
          width: "32px",
          height: "32px",
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
  isLoading: PropTypes.bool,
  user: PropTypes.oneOfType([PropTypes.bool, PropTypes.object]),
  settingsLink: PropTypes.object,
};

export default RightLink;
