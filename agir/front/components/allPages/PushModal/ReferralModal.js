import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

import Button from "@agir/front/genericComponents/Button";
import Modal from "@agir/front/genericComponents/Modal";

const StyledModalContent = styled.div`
  text-align: center;
  display: flex;
  flex-flow: column nowrap;
  align-items: center;
  justify-content: center;
  max-width: 600px;
  min-height: 441px;
  padding: 36px 40px;
  margin: 60px auto 0;
  box-shadow: ${style.elaborateShadow};
  border-radius: 8px;
  background-color: ${style.white};

  @media (max-width: ${style.collapse}px) {
    margin-top: 20px;
    min-height: 510px;
    max-width: calc(100% - 40px);
    padding: 36px 25px;
  }

  img {
    width: auto;
    height: auto;
    max-width: 100%;
    max-height: ${({ imgHeight }) => imgHeight || 126}px;
    margin-bottom: 25px;

    @media (max-width: ${style.collapse}px) {
      margin-bottom: 16px;
      background-position: bottom center;
    }
  }

  h2 {
    font-size: 20px;
    line-height: 1.5;
    margin-bottom: 16px;
    margin-top: 0;

    em {
      color: ${style.primary500};
    }

    a {
      color: inherit;
      text-decoration: underline;
    }
  }

  p {
    font-size: 1rem;
    line-height: 1.6;
    margin-bottom: 25px;
  }
`;

export const ReferralModal = ({ shouldShow = false, onClose }) => {
  return (
    <Modal shouldShow={shouldShow}>
      <StyledModalContent>
        <h2>Partagez !</h2>
        <p>Partagez ! Partagez ! Partagez !</p>
        <Button color="primary" onClick={onClose}>
          Fermer
        </Button>
      </StyledModalContent>
    </Modal>
  );
};
ReferralModal.propTypes = {
  shouldShow: PropTypes.bool,
  onClose: PropTypes.func,
};

export default ReferralModal;
