import PropTypes from "prop-types";
import React, { useState } from "react";
import useSWR from "swr";
import {
  updateMessageNotification,
  getGroupEndpoint,
} from "@agir/groups/api.js";

import styled from "styled-components";
import style from "@agir/front/genericComponents/_variables.scss";
import Button from "@agir/front/genericComponents/Button";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";
import { useToast } from "@agir/front/globalContext/hooks";
import { useIsDesktop } from "@agir/front/genericComponents/grid";

const StyledMuteButton = styled.div`
  cursor: pointer;
  ${({ disabled }) => (!disabled ? `opacity: 1;` : `opacity: 0.5;`)}

  ${RawFeatherIcon} {
    ${({ isMuted }) => (!isMuted ? `color: black;` : `color: ${style.redNSP};`)}
  }
  ${RawFeatherIcon}:hover {
    color: ${style.primary500};
  }
`;

const ButtonMuteMessage = ({ message }) => {
  const sendToast = useToast();
  const isDesktop = useIsDesktop();
  const [isMutedLoading, setIsMutedLoading] = useState(false);

  const { data: isMuted, mutate } = useSWR(
    getGroupEndpoint("messageNotification", { messagePk: message?.id })
  );

  const switchNotificationMessage = async () => {
    setIsMutedLoading(true);
    const { data } = await updateMessageNotification(message?.id, !isMuted);
    setIsMutedLoading(false);

    mutate(() => data, false);
    const text = data
      ? "Les notifications reliées à ce fil de message sont réactivées"
      : "Vous ne recevrez plus de notifications reliées à ce fil de messages";
    const type = data ? "SUCCESS" : "INFO";
    sendToast(text, type, { autoClose: true });
  };

  if (!isDesktop) {
    return (
      <StyledMuteButton
        isMuted={isMuted}
        disabled={typeof isMuted === "undefined" || isMutedLoading}
        onClick={!isMutedLoading && switchNotificationMessage}
      >
        <RawFeatherIcon name={`bell${isMuted ? "-off" : ""}`} />
      </StyledMuteButton>
    );
  }

  return (
    <Button
      small
      color="choose"
      disabled={typeof isMuted === "undefined" || isMutedLoading}
      onClick={!isMutedLoading && switchNotificationMessage}
    >
      <RawFeatherIcon
        width="1rem"
        height="1rem"
        name={`bell${isMuted ? "-off" : ""}`}
      />
      &nbsp;{isMuted ? "Réactiver" : "Rendre muet"}
    </Button>
  );
};
ButtonMuteMessage.propTypes = {
  message: PropTypes.shape({
    id: PropTypes.string.isRequired,
  }).isRequired,
};

export default ButtonMuteMessage;
