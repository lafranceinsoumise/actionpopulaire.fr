import PropTypes from "prop-types";
import React, { useState, useMemo } from "react";
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

const StyledMuteButton = styled.div`
  cursor: pointer;
  ${({ disabled }) => (!disabled ? `opacity: 1;` : `opacity: 0.5;`)}
  ${RawFeatherIcon} {
    ${({ isMuted }) => isMuted && `color: ${style.redNSP};`}
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

  const { data: isMuted, mutate } = useSWRImmutable(
    getGroupEndpoint("messageNotification", { messagePk: message?.id })
  );

  const switchNotificationMessage = async () => {
    setIsMutedLoading(true);
    const { data: muted } = await updateMessageNotification(
      message?.id,
      !isMuted
    );
    setIsMutedLoading(false);
    setIsModalOpen(false);

    mutate(() => muted, false);
    const text = muted
      ? "Vous ne recevrez plus de notifications reliées à ce fil de messages"
      : "Les notifications reliées à ce fil de message sont réactivées";
    const type = muted ? "INFO" : "SUCCESS";
    sendToast(text, type, { autoClose: true });
  };

  const handleSwitchNotification = () => {
    if (isMutedLoading) {
      return;
    }
    // Dont show modal to enable notification
    if (isMuted) {
      switchNotificationMessage();
      return;
    }
    setIsModalOpen(true);
  };

  const disabled = typeof isMuted === "undefined" || isMutedLoading;

  const CustomModal = useMemo(
    () => () =>
      (
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
      ),
    [isModalOpen]
  );

  if (!isDesktop) {
    return (
      <>
        <StyledMuteButton
          isMuted={isMuted}
          disabled={disabled}
          onClick={handleSwitchNotification}
        >
          <RawFeatherIcon name={`bell${isMuted ? "-off" : ""}`} />
        </StyledMuteButton>
        <CustomModal />
      </>
    );
  }

  return (
    <>
      <Button
        small
        color="choose"
        disabled={disabled}
        onClick={handleSwitchNotification}
      >
        <RawFeatherIcon
          width="1rem"
          height="1rem"
          name={`bell${isMuted ? "-off" : ""}`}
        />
        &nbsp;{isMuted ? "Réactiver" : "Rendre muet"}
      </Button>
      <CustomModal />
    </>
  );
};

ButtonMuteMessage.propTypes = {
  message: PropTypes.shape({
    id: PropTypes.string.isRequired,
  }).isRequired,
};

export default ButtonMuteMessage;
