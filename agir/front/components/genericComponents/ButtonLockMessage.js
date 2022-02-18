import PropTypes from "prop-types";
import React, { useState, useMemo } from "react";
import styled from "styled-components";
import useSWR, { mutate } from "swr";

import style from "@agir/front/genericComponents/_variables.scss";

import Button from "@agir/front/genericComponents/Button";
import ModalConfirmation from "@agir/front/genericComponents/ModalConfirmation";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";
import Spacer from "@agir/front/genericComponents/Spacer";

import { useIsDesktop } from "@agir/front/genericComponents/grid";
import { useToast } from "@agir/front/globalContext/hooks";

import { updateMessageLock, getGroupEndpoint } from "@agir/groups/api";
import { MANUAL_REVALIDATION_SWR_CONFIG } from "@agir/front/allPages/SWRContext";

const StyledButton = styled.div`
  cursor: pointer;
  ${({ disabled }) => (!disabled ? `opacity: 1;` : `opacity: 0.5;`)}
  ${RawFeatherIcon} {
    ${({ isLocked }) => isLocked && `color: ${style.redNSP};`}
  }

  @media (min-width: ${style.collapse}px) {
    ${RawFeatherIcon}:hover {
      color: ${style.primary500};
    }
  }
`;

const ButtonLockMessage = ({ message }) => {
  const sendToast = useToast();
  const isDesktop = useIsDesktop();
  const [isLockedLoading, setIsLockedLoading] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const { data: isLocked, mutate: mutateLocked } = useSWR(
    getGroupEndpoint("messageLocked", { messagePk: message?.id }),
    MANUAL_REVALIDATION_SWR_CONFIG
  );

  const switchLockedMessage = async () => {
    setIsLockedLoading(true);
    const { data: locked } = await updateMessageLock(message?.id, !isLocked);
    setIsLockedLoading(false);
    setIsModalOpen(false);

    mutateLocked(() => locked, false);
    // mutate(`/messages/${message.id}/`);
    // mutateMessages();
    mutate(`/api/groupes/messages/${message?.id}/`);

    const text = locked
      ? "Le fil de conversation est verrouillé"
      : "Le fil de conversation est déverrouillé";
    sendToast(text, "INFO", { autoClose: true });
  };

  const handleSwitchNotification = () => {
    if (isLockedLoading) {
      return;
    }
    // Dont show modal to enable lock
    if (isLocked) {
      switchLockedMessage();
      return;
    }
    setIsModalOpen(true);
  };

  const disabled = typeof isLocked === "undefined" || isLockedLoading;

  const CustomModal = useMemo(
    () => () =>
      (
        <ModalConfirmation
          title="Verrouiller cette conversation ?"
          confirmationLabel="Verrouiller"
          dismissLabel="Annuler"
          shouldShow={isModalOpen}
          onConfirm={switchLockedMessage}
          onClose={() => setIsModalOpen(false)}
          shouldDismissOnClick={false}
        >
          <Spacer size="1rem" />
          Le fil de discission sera verrouiler, personne ne pourra plus y
          envoyer de message.
          <Spacer size="0.5rem" />
          Vous pourrez le déverrouiller à tout moment.
        </ModalConfirmation>
      ),
    [isModalOpen]
  );

  if (!isDesktop) {
    return (
      <>
        <StyledButton
          isLocked={isLocked}
          disabled={disabled}
          onClick={handleSwitchNotification}
        >
          <RawFeatherIcon name={`bell${isLocked ? "-off" : ""}`} />
        </StyledButton>
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
          name={`${isLocked ? "un" : ""}lock`}
        />
        &nbsp;{isLocked ? "Déverrouiller" : "Verrouiller"}
      </Button>
      <CustomModal />
    </>
  );
};

ButtonLockMessage.propTypes = {
  message: PropTypes.shape({
    id: PropTypes.string.isRequired,
  }).isRequired,
};

export default ButtonLockMessage;
