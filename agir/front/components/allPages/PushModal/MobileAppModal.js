import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

import AppStore from "@agir/front/genericComponents/AppStore";
import Modal from "@agir/front/genericComponents/Modal";
import Spacer from "@agir/front/genericComponents/Spacer";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";

import modalImage from "./images/mobile-app-modal-bg.svg";
import modalLogo from "./images/modal-app-modal-logo.svg";

const CloseButton = styled.button``;

const Buttons = styled.div``;

const StyledModalContent = styled.div`
  position: relative;
  text-align: center;
  display: flex;
  flex-flow: column nowrap;
  align-items: center;
  justify-content: flex-start;
  max-width: 600px;
  padding: 0 0 36px;
  margin: 60px auto 0;
  box-shadow: ${style.elaborateShadow};
  border-radius: 8px;
  background-color: ${style.white};
  overflow-x: hidden;
  overflow-y: auto;

  @media (max-width: ${style.collapse}px) {
    margin-top: 20px;
    max-width: calc(100% - 40px);
    padding: 3rem 0;
  }

  & > * {
    margin: 0;
    padding: 0 3.375rem;

    @media (max-width: ${style.collapse}px) {
      padding: 0 1.5rem;
    }
  }

  ${CloseButton} {
    position: absolute;
    top: 1rem;
    right: 1rem;
    padding: 0;
    color: ${style.black1000};
    z-index: 1;
    background-color: transparent;
    border: none;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
  }

  header {
    position: relative;
    width: 100%;
    height: 177px;
    background-color: ${style.secondary500};
    background-image: url(${modalImage});
    background-position: bottom center;
    background-repeat: no-repeat;
    margin-bottom: 56px;

    &::after {
      content: "";
      display: block;
      background-color: transparent;
      background-image: url(${modalLogo});
      background-repeat: no-repeat;
      background-size: cover;
      width: 100px;
      height: 100px;
      position: absolute;
      bottom: 0;
      left: 50%;
      transform: translate3d(-50%, 50%, 0);
    }

    @media (max-width: ${style.collapse}px) {
      display: none;
    }
  }

  h4 {
    height: 2rem;
    font-size: 1rem;
    color: ${style.primary500};
    text-transform: uppercase;
  }

  h2 {
    font-size: 1.25rem;
    line-height: 1.5;
    font-weight: 700;
    padding-bottom: 1rem;
  }

  p {
    font-size: 1rem;
    line-height: 1.6;
    padding-bottom: 2.5rem;
  }

  ${Buttons} {
    display: flex;
    align-items: stretch;
    text-align: center;

    @media (max-width: ${style.collapse}px) {
      display: block;
    }
  }
`;

const UTM_PARAMS = {
  utm_source: "ap",
  utm_campaign: "mobile-app-modal",
};

export const MobileAppModal = ({ shouldShow = false, onClose }) => {
  return (
    <Modal shouldShow={shouldShow}>
      <StyledModalContent>
        <CloseButton onClick={onClose} aria-label="Fermer la modale">
          <RawFeatherIcon name="x" width="2rem" height="2rem" />
        </CloseButton>
        <header aria-hidden="true" />
        <h4>Nouveau</h4>
        <h2>L’application Action Populaire !</h2>
        <p>
          Recevez toutes les notifications sur votre téléphone et ne manquez
          aucune information près de chez vous !
        </p>
        <Buttons>
          <AppStore type="google" params={UTM_PARAMS} />
          <Spacer size="1rem" />
          <AppStore type="apple" params={UTM_PARAMS} />
        </Buttons>
      </StyledModalContent>
    </Modal>
  );
};
MobileAppModal.propTypes = {
  shouldShow: PropTypes.bool,
  onClose: PropTypes.func,
};

export default MobileAppModal;
