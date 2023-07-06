import PropTypes from "prop-types";
import React, { useCallback, useMemo, useState } from "react";
import styled from "styled-components";
import { mutate } from "swr";

import style from "@agir/front/genericComponents/_variables.scss";

import Button from "@agir/front/genericComponents/Button";
import Modal from "@agir/front/genericComponents/Modal";
import Spacer from "@agir/front/genericComponents/Spacer";

import imageNSP from "@agir/front/genericComponents/images/subscription_type__nsp.jpg";
import imageLFI from "@agir/front/genericComponents/logos/LFI-NUPES-Violet-H.webp";

import { updateProfile } from "./api";

const StyledModalContent = styled.div`
  text-align: center;
  display: flex;
  flex-flow: column nowrap;
  align-items: center;
  justify-content: flex-start;
  max-width: 600px;
  padding: 0 0 2.75rem;
  margin: 40px auto 0;
  box-shadow: ${style.elaborateShadow};
  background-color: ${style.white};
  overflow-x: hidden;
  overflow-y: auto;

  @media (max-width: ${style.collapse}px) {
    margin-top: 20px;
    min-height: 0;
    max-width: calc(100% - 40px);
  }

  & > * {
    width: 100%;
    padding: 0 40px;

    @media (max-width: ${style.collapse}px) {
      padding: 0 25px;
    }
  }

  img {
    width: ${({ $type }) => ($type === "LFI" ? "60%" : "100%")};
    height: auto;
    padding: 0;
    padding-top: ${({ $type }) => ($type === "LFI" ? "58px" : "0")};
    padding-bottom: ${({ $type }) => ($type === "LFI" ? "11px" : "0")};
  }

  h3 {
    font-size: 1.625rem;
    font-weight: 700;
    line-height: 1.5;
    text-align: center;
    margin: 0;
    padding-top: 2rem;
    padding-bottom: 1rem;

    @media (max-width: ${style.collapse}px) {
      font-size: 1.25rem;
    }
  }

  p {
    margin: 0;
    padding-bottom: 2rem;
  }

  ${Button} {
    max-width: 356px;
    width: 100%;
    flex-wrap: wrap;
    white-space: normal;
  }
`;

const SUBSCRIPTION_TYPE = {
  NSP: {
    image: imageNSP,
    title: "Soutenez la campagne présidentielle",
    confirmLabel: "Je soutiens !",
    confirmColor: style.redNSP,
    target: {
      event: "participer à cet événement",
      group: "rejoindre ce groupe",
    },
    content:
      "Vous êtes membre de la France Insoumise mais vous n’avez pas encore soutenu la campagne de Jean-Luc Mélenchon pour 2022. Confirmez votre soutien",
    update: {
      is2022: true,
    },
  },
  LFI: {
    image: imageLFI,
    title: "Rejoignez la France insoumise",
    confirmLabel: "Je rejoins la France Insoumise",
    confirmColor: style.redLFI,
    target: {
      event: "participer à cet événement",
      group: "rejoindre ce groupe d'action",
    },
    content:
      "L’inscription est réservée aux membres de la France Insoumise. Confirmez que vous souhaitez rejoindre le mouvement",
    update: {
      isInsoumise: true,
    },
  },
};

export const SubscriptionTypeModal = (props) => {
  const { type, target, onConfirm, onCancel, shouldShow, isLoading } = props;
  const { image, title, content, confirmLabel } = SUBSCRIPTION_TYPE[type];
  const targetLabel = SUBSCRIPTION_TYPE[type].target[target];

  return (
    <Modal shouldShow={shouldShow}>
      <StyledModalContent $type={type}>
        <img src={image} alt={title} />
        <h3>
          {title} pour {targetLabel}
        </h3>
        <p>
          {content} pour {targetLabel}.
        </p>
        <footer>
          <Button onClick={onConfirm} disabled={isLoading} color="primary">
            {confirmLabel}
          </Button>
          <Spacer size="1.5rem" />
          <button
            style={{
              background: "transparent",
              border: "none",
              cursor: isLoading ? "default" : "pointer",
            }}
            onClick={onCancel}
            disabled={isLoading}
          >
            Annuler
          </button>
        </footer>
      </StyledModalContent>
    </Modal>
  );
};

const StandaloneSubscriptionTypeModal = (props) => {
  const { type, onConfirm } = props;
  const [isLoading, setIsLoading] = useState(props.isLoading);

  const update = useMemo(() => SUBSCRIPTION_TYPE[type].update, [type]);
  const handleConfirm = useCallback(async () => {
    setIsLoading(true);
    await updateProfile(update);
    onConfirm();
    setIsLoading(false);
    mutate("/api/session/");
  }, [update, onConfirm]);

  return (
    <SubscriptionTypeModal
      {...props}
      isLoading={props.isLoading || isLoading}
      onConfirm={handleConfirm}
    />
  );
};

StandaloneSubscriptionTypeModal.propTypes = SubscriptionTypeModal.propTypes = {
  type: PropTypes.oneOf(Object.keys(SUBSCRIPTION_TYPE)).isRequired,
  target: PropTypes.oneOf(["event", "group"]).isRequired,
  onConfirm: PropTypes.func.isRequired,
  onCancel: PropTypes.func.isRequired,
  shouldShow: PropTypes.bool,
  isLoading: PropTypes.bool,
};

export default StandaloneSubscriptionTypeModal;
