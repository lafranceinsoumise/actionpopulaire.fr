import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

import Modal from "@agir/front/genericComponents/Modal";
import Button from "@agir/front/genericComponents/Button";
import Spacer from "@agir/front/genericComponents/Spacer";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";
import promo1 from "./promo-message1.svg";
import promo2 from "./promo-message2.svg";
import promo3 from "./promo-message3.svg";
import promo4 from "./promo-message4.svg";

const CloseButton = styled.button``;

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
    padding: 0 0 1.5rem;
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
    background-position: bottom center;
    background-repeat: no-repeat;
    margin-bottom: 56px;

    @media (max-width: ${style.collapse}px) {
      height: 100px;
      background-size: 160px auto;
    }

    &::after {
      content: "";
      display: block;
      background-color: transparent;
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

    @media (max-width: ${style.collapse}px) {
      font-size: 0.875rem;
    }
  }
`;

const Container = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  flex-direction: column;
  padding: 2rem;
  overflow-y: auto;

  p {
    margin: 50px 0;
    font-size: 18px;
  }
`;

const StyledLabel = styled.div`
  color: ${style.redNSP};
`;

const Title = styled.div`
  margin: 0.5rem 0;
  font-size: 1.5rem;
  font-weight: 700;
`;

export const PromoMessageModal = ({ shouldShow = false, onClose }) => {

  return (
    <Container>
      <StyledLabel>Nouveau</StyledLabel>
      <Title>La messagerie de votre groupe</Title>
      <img src={promo1} />
      <p>
        <b>Lancez une première conversation dans votre groupe !</b>
        <br/>
        Discustez de vos prochaines actions sur Action Populaire
      </p>
      <Button color="primary">
        <RawFeatherIcon name="edit" width="1.5rem" height="1.5rem" style={{marginRight:"0.5rem"}}/>Nouveau message de groupe
      </Button>
    </Container>
  );


  return (
    <Modal shouldShow={shouldShow} onClose={onClose}>
      <StyledModalContent>
        <CloseButton onClick={onClose} aria-label="Fermer la modale">
          <RawFeatherIcon name="x" width="2rem" height="2rem" />
        </CloseButton>

        {/* <header aria-hidden="true" />
        <h4>Nouveau</h4>
        <h2>L’application Action Populaire !</h2>
        <p>
          Recevez toutes les notifications sur votre téléphone et ne manquez
          aucune information près de chez vous !
        </p> */}

        <h1>La messagerie de votre groupe</h1>
        <img src="" />
        <h3>
          <b>Lancez une première conversation dans votre groupe !</b>
          <br/>
          Discustez de vos prochaines actions sur Action Populaire
        </h3>   
        {/* <Button>Nouveau message de groupe</Button> */}
     
      </StyledModalContent>
      
    </Modal>
  );
};

PromoMessageModal.propTypes = {
  shouldShow: PropTypes.bool,
  onClose: PropTypes.func,
};

export default PromoMessageModal;
