import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

import AppStore from "@agir/front/genericComponents/AppStore";
import Modal from "@agir/front/genericComponents/Modal";
import Spacer from "@agir/front/genericComponents/Spacer";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";

import modalImage from "./images/mobile-app-modal-bg.png";
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
  box-shadow: ${(props) => props.theme.elaborateShadow};
  border-radius: ${(props) => props.theme.borderRadius};
  background-color: ${(props) => props.theme.white};
  overflow-x: hidden;
  overflow-y: auto;

  @media (max-width: ${(props) => props.theme.collapse}px) {
    margin-top: 20px;
    max-width: calc(100% - 40px);
    padding: 0 0 1.5rem;
  }

  & > * {
    margin: 0;
    padding: 0 3.375rem;

    @media (max-width: ${(props) => props.theme.collapse}px) {
      padding: 0 1.5rem;
    }
  }

  ${CloseButton} {
    position: absolute;
    top: 1rem;
    right: 1rem;
    padding: 0;
    color: ${(props) => props.theme.black1000};
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
    background-color: ${(props) => props.theme.secondary500};
    background-image: url(${modalImage});
    background-position: bottom center;
    background-repeat: no-repeat;
    margin-bottom: 56px;

    @media (max-width: ${(props) => props.theme.collapse}px) {
      height: 100px;
      background-size: 160px auto;
    }

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
  }

  h4 {
    height: 2rem;
    font-size: 1rem;
    color: ${(props) => props.theme.primary500};
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

    @media (max-width: ${(props) => props.theme.collapse}px) {
      font-size: 0.875rem;
    }
  }

  ${Buttons} {
    display: flex;
    align-items: stretch;
    text-align: center;

    @media (max-width: ${(props) => props.theme.collapse}px) {
      display: block;
    }
  }
`;

export const MobileAppModal = ({ shouldShow = false, onClose }) => {
  return (
    <Modal shouldShow={shouldShow} onClose={onClose}>
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
          <AppStore type="google" />
          <Spacer size="1rem" />
          <AppStore type="apple" />
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
