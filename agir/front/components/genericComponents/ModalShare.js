import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import Button from "@agir/front/genericComponents/Button";
import Modal from "@agir/front/genericComponents/Modal";
import ShareContentUrl from "@agir/front/genericComponents/ShareContentUrl";

const ModalContainer = styled.div`
  background: ${(props) => props.theme.background0};
  width: 40%;
  width: fit-content;
  margin: 5% auto;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  border-radius: ${(props) => props.theme.borderRadius};

  @media (max-width: ${(props) => props.theme.collapse}px) {
    width: 90%;
  }
`;

const ModalContent = styled.div`
  display: inline-flex;
  flex-direction: column;
  padding: 1rem;

  h1 {
    font-size: 1rem;
  }

  > ${Button} {
    margin-bottom: 1rem;
  }
`;

const ModalShare = (props) => {
  const { shouldShow = false, onClose, url = window.location.href } = props;

  return (
    <Modal shouldShow={shouldShow} onClose={onClose}>
      <ModalContainer>
        <ModalContent>
          <h1>Partager la page</h1>
          <ShareContentUrl url={url} />
        </ModalContent>
      </ModalContainer>
    </Modal>
  );
};

ModalShare.propTypes = {
  shouldShow: PropTypes.bool,
  onClose: PropTypes.func,
  url: PropTypes.string,
};

export default ModalShare;
