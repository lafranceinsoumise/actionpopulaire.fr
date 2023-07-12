/* eslint-disable react/display-name */
import PropTypes from "prop-types";
import React, { useCallback, useMemo, useState } from "react";
import styled from "styled-components";
import { mutate } from "swr";
import useSWRImmutable from "swr/immutable";

import style from "@agir/front/genericComponents/_variables.scss";

import Button from "@agir/front/genericComponents/Button";
import ModalConfirmation from "@agir/front/genericComponents/ModalConfirmation";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";
import Spacer from "@agir/front/genericComponents/Spacer";

import { useIsDesktop } from "@agir/front/genericComponents/grid";
import { useToast } from "@agir/front/globalContext/hooks";

import { updateMessageLock, getGroupEndpoint } from "@agir/groups/utils/api";

const StyledButton = styled.button`
  background-color: transparent;
  padding: 0;
  margin: 0;
  border: none;
  cursor: pointer;
  ${({ disabled }) => (!disabled ? `opacity: 1;` : `opacity: 0.5;`)}
  ${RawFeatherIcon} {
    ${({ $isLocked }) => $isLocked && `color: ${style.redNSP};`}
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

  const messagePk = message?.id;
  const {
    data: isLocked,
    mutate: mutateLocked,
    isLoading,
  } = useSWRImmutable(getGroupEndpoint("messageLocked", { messagePk }), {
    fallbackData: !!message?.isLocked,
  });

  const switchLockedMessage = useCallback(async () => {
    setIsLockedLoading(true);
    const { data: locked } = await updateMessageLock(messagePk, !isLocked);
    setIsLockedLoading(false);
    setIsModalOpen(false);

    mutateLocked(() => locked, false);
    mutate(`/api/groupes/messages/${messagePk}/`);
    sendToast(
      locked
        ? "Le fil de conversation est verrouillé"
        : "Le fil de conversation est déverrouillé",
      "INFO",
      { autoClose: true },
    );
  }, [isLocked, messagePk, mutateLocked, sendToast]);

  const loading = isLoading || isLockedLoading;

  return (
    <>
      {isDesktop ? (
        <Button
          small
          color="choose"
          disabled={loading}
          loading={loading}
          onClick={() => !loading && setIsModalOpen(true)}
        >
          <RawFeatherIcon
            width="1rem"
            height="1rem"
            name={`${isLocked ? "un" : ""}lock`}
          />
          &nbsp;{isLocked ? "Déverrouiller" : "Verrouiller"}
        </Button>
      ) : (
        <StyledButton
          $isLocked={isLocked}
          disabled={loading}
          onClick={() => !loading && setIsModalOpen(true)}
        >
          <RawFeatherIcon name={`${!isLocked ? "un" : ""}lock`} />
        </StyledButton>
      )}

      <ModalConfirmation
        title={`Souhaitez-vous ${isLocked ? "dé" : ""}verrouiller cette
            conversation ?`}
        confirmationLabel={!isLocked ? "Verrouiller" : "Déverrouiller"}
        dismissLabel="Annuler"
        shouldShow={isModalOpen}
        onConfirm={switchLockedMessage}
        onClose={() => setIsModalOpen(false)}
        shouldDismissOnClick={false}
      >
        <Spacer size="1rem" />
        {!isLocked ? (
          <>
            Plus personne ne pourra y répondre.
            <Spacer size="0.5rem" />
            Les gestionnaires du groupe pourront déverrouiller la conversation
            n'importe quand.
          </>
        ) : (
          "Les participant·es pourront de nouveau y écrire des réponses"
        )}
      </ModalConfirmation>
    </>
  );
};

ButtonLockMessage.propTypes = {
  message: PropTypes.shape({
    id: PropTypes.string.isRequired,
    isLocked: PropTypes.bool,
  }).isRequired,
};

export default ButtonLockMessage;
