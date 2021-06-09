import PropTypes from "prop-types";
import React, { useMemo } from "react";
import styled from "styled-components";

import { addQueryStringParams } from "@agir/lib/utils/url";
import style from "@agir/front/genericComponents/_variables.scss";

import Button from "@agir/front/genericComponents/Button";
import Modal from "@agir/front/genericComponents/Modal";

import modalImage from "./images/referral-modal.jpg";

const Buttons = styled.div`
  display: flex;
  align-items: stretch;
  text-align: center;

  @media (max-width: ${style.collapse}px) {
    flex-flow: column nowrap;
  }

  & ${Button} {
    justify-content: center;
  }

  & ${Button} + ${Button} {
    margin-left: 1rem;

    @media (max-width: ${style.collapse}px) {
      margin-left: 0;
      margin-top: 0.5rem;
    }
  }
`;

const StyledModalContent = styled.div`
  text-align: center;
  display: flex;
  flex-flow: column nowrap;
  align-items: center;
  justify-content: flex-start;
  max-width: 600px;
  min-height: 441px;
  padding: 0 0 36px;
  margin: 60px auto 0;
  box-shadow: ${style.elaborateShadow};
  border-radius: 8px;
  background-color: ${style.white};
  overflow-x: hidden;
  overflow-y: auto;

  @media (max-width: ${style.collapse}px) {
    margin-top: 20px;
    min-height: 510px;
    max-width: calc(100% - 40px);
  }

  & > * {
    padding: 0 40px;

    @media (max-width: ${style.collapse}px) {
      padding: 0 25px;
    }
  }

  img {
    width: auto;
    height: auto;
    min-width: 100%;
    min-height: 126px;
    object-fit: cover;
    padding: 0;
    margin-bottom: 2rem;

    @media (max-width: ${style.collapse}px) {
      padding: 0;
    }
  }

  h2 {
    font-size: 20px;
    line-height: 1.5;
    margin-bottom: 16px;
    margin-top: 0;
  }

  p {
    font-size: 1rem;
    line-height: 1.6;
    margin-bottom: 25px;
  }
`;

const UTM_PARAMS = {
  utm_source: "ap",
  utm_campaign: "referral-modal",
};

export const ReferralModal = ({
  referralURL = "",
  shouldShow = false,
  onClose,
}) => {
  const href = useMemo(
    () => referralURL && addQueryStringParams(referralURL, UTM_PARAMS),
    [referralURL]
  );
  return (
    <Modal shouldShow={!!href && shouldShow}>
      <StyledModalContent>
        <img
          src={modalImage}
          width="1200"
          height="372"
          alt="Opération 300000 signatures !"
        />
        <h2>
          Récupérez votre lien d’invitation “Nous&nbsp;Sommes&nbsp;Pour&nbsp;!”
        </h2>
        <p>
          Partagez votre lien sur les réseaux sociaux et collectez un maximum de
          signatures !
        </p>
        <Buttons>
          <Button
            color="primary"
            as="a"
            href={href}
            target="_blank"
            rel="noopener noreferrer"
          >
            Partager mon lien
          </Button>
          <Button onClick={onClose}>Pas maintenant</Button>
        </Buttons>
      </StyledModalContent>
    </Modal>
  );
};
ReferralModal.propTypes = {
  referralURL: PropTypes.string,
  shouldShow: PropTypes.bool,
  onClose: PropTypes.func,
};

export default ReferralModal;
