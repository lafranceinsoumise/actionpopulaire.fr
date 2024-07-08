import PropTypes from "prop-types";
import React, { useState } from "react";

import Avatar from "@agir/front/genericComponents/Avatar";
import BottomSheet from "@agir/front/genericComponents/BottomSheet";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";
import Spacer from "@agir/front/genericComponents/Spacer";
import ButtonMuteMessage from "@agir/front/genericComponents/ButtonMuteMessage";
import ButtonLockMessage from "@agir/front/genericComponents/ButtonLockMessage";

import { MessageOptions } from "@agir/msgs/MessagePage/MessageThreadMenu";
import { IconLink } from "./StyledBar";
import UserMenu from "@agir/front/app/Navigation/TopBar/UserMenu";

export const RightLink = (props) => {
  const { isLoading, user, settingsLink } = props;
  const [isUserMenuOpen, setIsUserMenuOpen] = useState(false);

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

  // Show muted message settings
  if (
    settingsLink?.message &&
    settingsLink.message.id &&
    !settingsLink.message.readonly
  ) {
    const { message } = settingsLink;
    const isAuthor = message.author.id === user.id;
    const isManager = message.group?.isManager;

    return (
      <>
        {(isManager || isAuthor) && <ButtonLockMessage message={message} />}
        <Spacer size="1rem" style={{ display: "inline-block" }} />
        <ButtonMuteMessage message={message} />
      </>
    );
  }

  if (settingsLink?.messageSettings) {
    return <MessageOptions />;
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
        shouldDismissOnClick={false}
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
