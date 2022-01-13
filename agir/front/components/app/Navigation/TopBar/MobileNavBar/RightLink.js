import PropTypes from "prop-types";
import React, { useState } from "react";
import styled from "styled-components";

import Avatar from "@agir/front/genericComponents/Avatar";
import BottomSheet from "@agir/front/genericComponents/BottomSheet";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";
import Spacer from "@agir/front/genericComponents/Spacer";
import style from "@agir/front/genericComponents/_variables.scss";

import { IconLink } from "./StyledBar";
import UserMenu from "../UserMenu";
import useSWR from "swr";
import { useToast } from "@agir/front/globalContext/hooks";
import {
  updateMessageNotification,
  getGroupEndpoint,
} from "@agir/groups/api.js";
import { routeConfig } from "@agir/front/app/routes.config";

const BlockMuteMessage = styled.div`
  ${({ disabled }) => (!disabled ? `opacity: 1;` : `opacity: 0.5;`)}
  ${({ isMuted }) => !isMuted && `color: red;`}
  ${RawFeatherIcon}:hover {
    color: ${style.primary500};
  }
`;


export const RightLink = (props) => {
  const { isLoading, user, settingsLink } = props;
  const [isUserMenuOpen, setIsUserMenuOpen] = useState(false);
  const [isMutedLoading, setIsMutedLoading] = useState(false);
  const sendToast = useToast();

  let pathname = window.location.pathname;
  const matchMessagePage = routeConfig.messages.match(pathname);
  pathname = pathname.substr(0, pathname.length - 1);
  const messagePk = matchMessagePage
    ? pathname.substr(pathname.lastIndexOf("/") + 1)
    : undefined;
  const { data: isMuted, mutate } = useSWR(
    messagePk && getGroupEndpoint("messageNotification", { messagePk })
  );

  const switchNotificationMessage = async () => {
    setIsMutedLoading(true);
    const { data } = await updateMessageNotification(messagePk, !isMuted);
    setIsMutedLoading(false);

    mutate(() => data, false);
    const text = data
      ? "Les notifications reliées à ce fil de message sont réactivées"
      : "Vous ne recevrez plus de notifications reliées à ce fil de messages";
    const type = data ? "SUCCESS" : "INFO";
    sendToast(text, type, { autoClose: true });
  };

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

  if (settingsLink) {
    const isMessagePage = !!matchMessagePage;
    // Show muted message settings
    if (isMessagePage) {
      return (
        <BlockMuteMessage
          isMuted={isMuted}
          disabled={typeof isMuted === "undefined" || isMutedLoading}
          onClick={!isMutedLoading && switchNotificationMessage}
        >
          <RawFeatherIcon name={`bell${!isMuted ? "-off" : ""}`} />
        </BlockMuteMessage>
      );
    }

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
