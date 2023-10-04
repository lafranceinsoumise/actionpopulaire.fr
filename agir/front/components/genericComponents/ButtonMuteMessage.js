import PropTypes from "prop-types";
import React, { useState, useCallback } from "react";
import styled from "styled-components";
import useSWRImmutable from "swr/immutable";

import style from "@agir/front/genericComponents/_variables.scss";

import Button from "@agir/front/genericComponents/Button";
import ModalConfirmation from "@agir/front/genericComponents/ModalConfirmation";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";
import Spacer from "@agir/front/genericComponents/Spacer";

import { useIsDesktop } from "@agir/front/genericComponents/grid";
import { useToast } from "@agir/front/globalContext/hooks";

import {
  updateMessageNotification,
  getGroupEndpoint,
} from "@agir/groups/utils/api";

const StyledMuteButton = styled.button`
  background-color: transparent;
  padding: 0;
  margin: 0;
  border: none;
  cursor: pointer;
  ${({ disabled }) => (!disabled ? `opacity: 1;` : `opacity: 0.5;`)}
  ${RawFeatherIcon} {
    ${({ $isMuted }) => $isMuted && `color: ${style.redNSP};`}
  }

  @media (min-width: ${style.collapse}px) {
    ${RawFeatherIcon}:hover {
      color: ${style.primary500};
    }
  }
`;

const ButtonMuteMessage = ({ message }) => {
  const sendToast = useToast();
  const isDesktop = useIsDesktop();
  const [isMutedLoading, setIsMutedLoading] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const messagePk = message?.id;

  const {
    data: isMuted,
    isLoading,
    mutate,
  } = useSWRImmutable(getGroupEndpoint("messageNotification", { messagePk }), {
    fallbackData: !!message?.isMuted,
  });

  const switchNotificationMessage = useCallback(async () => {
    setIsMutedLoading(true);
    const { data: muted } = await updateMessageNotification(
      messagePk,
      !isMuted,
    );
    setIsMutedLoading(false);
    setIsModalOpen(false);
    mutate(() => muted, false);

    sendToast(
      muted
        ? "Vous ne recevrez plus de notifications reliées à ce fil de messages"
        : "Les notifications reliées à ce fil de message sont réactivées",
      "INFO",
      { autoClose: true },
    );
  }, [isMuted, messagePk, mutate, sendToast]);

  const handleSwitchNotification = useCallback(() => {
    if (isMutedLoading) {
      return;
    }
    // Dont show modal to enable notification
    if (isMuted) {
      switchNotificationMessage();
      return;
    }
    setIsModalOpen(true);
  }, [isMuted, isMutedLoading, switchNotificationMessage]);

  const loading = isLoading || isMutedLoading;

  return (
    <>
      {isDesktop ? (
        <Button
          small
          color="choose"
          icon={`bell${isMuted ? "-off" : ""}`}
          disabled={loading}
          loading={loading}
          onClick={handleSwitchNotification}
        >
          {isMuted ? "Réactiver" : "Rendre muet"}
        </Button>
      ) : (
        <StyledMuteButton
          $isMuted={isMuted}
          disabled={loading}
          onClick={handleSwitchNotification}
        >
          <RawFeatherIcon name={`bell${isMuted ? "-off" : ""}`} />
        </StyledMuteButton>
      )}
      <ModalConfirmation
        title="Rendre muet cette conversation ?"
        confirmationLabel="Rendre muet"
        dismissLabel="Annuler"
        shouldShow={isModalOpen}
        onConfirm={switchNotificationMessage}
        onClose={() => setIsModalOpen(false)}
        shouldDismissOnClick={false}
      >
        <Spacer size="1rem" />
        Vous ne recevrez plus de notifications et e-mails concernant cette
        conversation.
        <Spacer size="0.5rem" />
        Vous pourrez réactiver les notifications et e-mails à tout moment
      </ModalConfirmation>
    </>
  );
};

ButtonMuteMessage.propTypes = {
  message: PropTypes.shape({
    id: PropTypes.string.isRequired,
    isMuted: PropTypes.bool,
  }).isRequired,
};

export default ButtonMuteMessage;
