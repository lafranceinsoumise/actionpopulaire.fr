import PropTypes from "prop-types";
import React, { useCallback, useMemo, useState } from "react";
import styled from "styled-components";

import Button from "@agir/front/genericComponents/Button";
import Modal from "@agir/front/genericComponents/Modal";
import Spacer from "@agir/front/genericComponents/Spacer";

import { routeConfig } from "@agir/front/app/routes.config";

const StyledModalContent = styled.div`
  max-width: 600px;
  padding: 1rem;
  margin: 40px auto 0;
  border-radius: ${(props) => props.theme.borderRadius};
  box-shadow: ${(props) => props.theme.elaborateShadow};
  background-color: ${(props) => props.theme.white};

  @media (max-width: ${(props) => props.theme.collapse}px) {
    margin-top: 1rem;
    min-height: 0;
    max-width: calc(100% - 2rem);
  }

  h3,
  h6 {
    text-align: center;
    line-height: 1.5;
    margin: 0;
  }

  h3 {
    font-weight: 600;
    font-size: 1.25rem;
  }

  h6 {
    color: ${(props) => props.theme.primary500};
    font-weight: 400;
    font-size: 0.875rem;
  }

  footer {
    width: 100%;
  }
`;

export const SoftLoginModal = (props) => {
  const { user, shouldShow, onClose } = props;

  const username =
    user?.displayName.length > 2
      ? user?.displayName
      : user?.firstName || user?.displayName;

  return (
    <Modal shouldShow={!!user && shouldShow} noScroll>
      <StyledModalContent>
        <h3>Bonjour {username}</h3>
        <h6>{user.email}</h6>
        <Spacer size="0.625rem" />
        <p>Êtes-vous bien {username}&nbsp;?</p>
        <p>
          Vous avez été connecté·e automatiquement car vous avez suivi un lien
          qui lui a été envoyé par email.
        </p>
        <Spacer size=".5rem" />
        <footer>
          <Button block onClick={onClose} color="primary">
            Je suis {username}
          </Button>
          <Spacer size="0.5rem" />
          <Button block link href={routeConfig.logout.getLink()}>
            Ce n'est pas moi
          </Button>
        </footer>
      </StyledModalContent>
    </Modal>
  );
};

SoftLoginModal.propTypes = {
  user: PropTypes.shape({
    displayName: PropTypes.string.isRequired,
    firstName: PropTypes.string,
    email: PropTypes.string.isRequired,
  }).isRequired,
  shouldShow: PropTypes.bool.isRequired,
  onClose: PropTypes.func.isRequired,
};

export default SoftLoginModal;
