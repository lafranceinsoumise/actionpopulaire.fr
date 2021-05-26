import PropTypes from "prop-types";
import React, { useEffect, useMemo, useState, useRef } from "react";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

import Button from "@agir/front/genericComponents/Button";
import ModalWrapper from "@agir/front/genericComponents/Modal";

const StyledModalBody = styled.div`
  h4 {
    margin-top: 0;
    margin-bottom: 1rem;
    font-size: 1rem;
    font-weight: 600;
    line-height: 1.5;
  }

  p {
    margin: 0;
    padding: 0;
    font-size: 0.875rem;
    line-height: 1.5;

    strong {
      font-weight: 600;
    }
  }

  p + p {
    margin-top: 0.25rem;
  }
`;
const StyledModalFooter = styled.footer`
  display: flex;
  margin-top: 1.5rem;
  flex-flow: ${({ $inline }) => ($inline ? "row nowrap" : "column nowrap")};

  ${Button} {
    flex: 1 1 auto;
    justify-content: center;
    transition: opacity 250ms ease-in-out;
  }

  ${Button} + ${Button} {
    margin: ${({ $inline }) => ($inline ? "0 0 0 .5rem" : ".5rem 0 0")};
  }
`;
const StyledModalContent = styled.div`
  max-width: 415px;
  margin: 40px auto;
  background-color: ${style.white};
  border-radius: 8px;
  padding: 1rem;

  @media (max-width: ${style.collapse}px) {
    margin: 0;
    border-radius: 0;
    max-width: 100%;
    min-height: 100vh;
  }
`;

const Steps = {
  delete: [
    ({ isLoading, onClose, onDelete }) => (
      <>
        <StyledModalBody>
          <h4>Supprimer ce message ?</h4>
          <p>
            Ce message <strong>disparaîtra</strong> de la discussion et plus
            personne ne pourra le voir.
          </p>
          <p>
            Il n'est pas possible d'annuler cette opération. Tout abus sera
            sanctionné.
          </p>
        </StyledModalBody>
        <StyledModalFooter $inline>
          <Button color="default" onClick={onClose} disabled={isLoading}>
            Annuler
          </Button>
          <Button
            color="danger"
            icon="trash-2"
            onClick={onDelete}
            disabled={isLoading}
          >
            Supprimer
          </Button>
        </StyledModalFooter>
      </>
    ),
    ({ isLoading, onClose, onReport }) => (
      <>
        <StyledModalBody>
          <h4>Le message a été supprimé</h4>
          {onReport ? (
            <p>
              Ce compte enfreint les règles de Action Populaire ?
              <br />
              Notre équipe sera notifiée de votre signalement.
            </p>
          ) : null}
        </StyledModalBody>
        <StyledModalFooter>
          {onReport ? (
            <Button
              color="danger"
              icon="flag"
              onClick={onReport}
              disabled={isLoading}
            >
              Signaler
            </Button>
          ) : null}
          <Button color="default" onClick={onClose} disabled={isLoading}>
            {onReport ? "Non merci" : "Terminer"}
          </Button>
        </StyledModalFooter>
      </>
    ),
    ({ onClose }) => (
      <>
        <StyledModalBody>
          <h4>Notre équipe a reçu votre signalement</h4>
        </StyledModalBody>
        <StyledModalFooter>
          <Button color="default" onClick={onClose}>
            Terminer
          </Button>
        </StyledModalFooter>
      </>
    ),
  ],
  report: [
    ({ isLoading, onClose, onReport }) => (
      <>
        <StyledModalBody>
          <h4>Signaler ce message ?</h4>
          <p>
            <strong>Notre équipe sera notifiée</strong> de votre signalement.
          </p>
          <p>
            Il n'est pas possible d'annuler cette opération. Tout abus sera
            sanctionné.
          </p>
        </StyledModalBody>
        <StyledModalFooter $inline>
          <Button color="default" onClick={onClose} disabled={isLoading}>
            Annuler
          </Button>
          <Button
            color="danger"
            icon="flag"
            onClick={onReport}
            disabled={isLoading}
          >
            Signaler
          </Button>
        </StyledModalFooter>
      </>
    ),
    ({ isLoading, onClose, onDelete }) => (
      <>
        <StyledModalBody>
          <h4>Notre équipe a reçu votre signalement</h4>
          <p>
            Si nous constatons que ce message enfreint les règles de Action
            Populaire, nous prendrons les mesures nécessaire.
          </p>
          {onDelete ? (
            <p>
              <strong>
                En attendant, en tant que gestionnaire du groupe vous pouvez
                supprimer le message.
              </strong>{" "}
              Il disparaîtra et plus personne ne pourra le voir.
            </p>
          ) : null}
        </StyledModalBody>
        <StyledModalFooter>
          {onDelete ? (
            <Button
              color="danger"
              icon="trash-2"
              onClick={onDelete}
              disabled={isLoading}
            >
              Supprimer
            </Button>
          ) : null}
          <Button color="default" onClick={onClose} disabled={isLoading}>
            {onDelete ? "Non merci" : "Terminer"}
          </Button>
        </StyledModalFooter>
      </>
    ),
    ({ onClose }) => (
      <>
        <StyledModalBody>
          <h4>Le message a été supprimé</h4>
        </StyledModalBody>
        <StyledModalFooter>
          <Button color="default" onClick={onClose}>
            Terminer
          </Button>
        </StyledModalFooter>
      </>
    ),
  ],
};

const MessageActionModal = (props) => {
  const { action, shouldShow, onClose, onDelete, onReport, isLoading, error } =
    props;
  const [step, setStep] = useState(0);
  const nextStep = useRef(0);
  const lastStep = useRef(null);

  const Step = useMemo(() => {
    const Step =
      action && Steps[action] ? Steps[action][step] : lastStep.current;
    lastStep.current = Step;
    return Step;
  }, [action, step]);

  const handleDelete = useMemo(
    () =>
      typeof onDelete === "function"
        ? () => {
            nextStep.current += 1;
            onDelete();
          }
        : undefined,
    [onDelete]
  );

  const handleReport = useMemo(
    () =>
      typeof onReport === "function"
        ? () => {
            nextStep.current += 1;
            onReport();
          }
        : undefined,
    [onReport]
  );

  useEffect(() => {
    if (!isLoading && step !== nextStep.current) {
      if (!error) {
        setStep(nextStep.current);
      } else {
        nextStep.current = step;
      }
    }
  }, [isLoading, error, step]);

  useEffect(() => {
    if (shouldShow) {
      setStep(0);
      nextStep.current = 0;
    }
  }, [shouldShow]);

  return (
    <ModalWrapper
      shouldShow={shouldShow && !!Step}
      onClose={isLoading ? undefined : onClose}
      noScroll
    >
      <StyledModalContent $isLoading={isLoading}>
        {Step ? (
          <Step
            onClose={onClose}
            onDelete={handleDelete}
            onReport={handleReport}
            isLoading={isLoading}
          />
        ) : null}
      </StyledModalContent>
    </ModalWrapper>
  );
};
MessageActionModal.propTypes = {
  action: PropTypes.oneOf(Object.keys(Steps)),
  error: PropTypes.string,
  isLoading: PropTypes.bool,
  shouldShow: PropTypes.bool,
  onClose: PropTypes.func,
  onDelete: PropTypes.func,
  onReport: PropTypes.func,
};
export default MessageActionModal;
