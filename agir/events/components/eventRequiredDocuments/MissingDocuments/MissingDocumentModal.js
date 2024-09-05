import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import Modal from "@agir/front/genericComponents/Modal";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";
import MissingDocuments from "./MissingDocuments";

const CloseButton = styled.button``;
const StyledModalContent = styled.div`
  max-width: 716px;
  position: relative;
  width: 100%;
  padding: 3rem;
  margin: 60px auto 0;
  box-shadow: ${(props) => props.theme.elaborateShadow};
  background-color: ${(props) => props.theme.background0};
  overflow-x: hidden;
  overflow-y: auto;

  @media (max-width: ${(props) => props.theme.collapse}px) {
    max-width: 100%;
    padding: 1.5rem;
    margin: 0;
    min-height: 100%;
  }

  ${CloseButton} {
    position: absolute;
    top: 3rem;
    right: 3rem;
    padding: 0;
    color: ${(props) => props.theme.text1000};
    z-index: 1;
    background-color: transparent;
    border: none;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;

    @media (max-width: ${(props) => props.theme.collapse}px) {
      top: 1.5rem;
      right: 1.5rem;
    }
  }
}`;

export const MissingDocumentModal = (props) => {
  const { shouldShow, onClose, projects, isBlocked } = props;

  return (
    <Modal shouldShow={shouldShow} onClose={onClose} noScroll>
      <StyledModalContent>
        {onClose && (
          <CloseButton onClick={onClose} aria-label="Fermer la modale">
            <RawFeatherIcon name="x" width="1.5rem" height="1.5rem" />
          </CloseButton>
        )}
        <MissingDocuments
          onClose={onClose}
          projects={projects}
          isBlocked={isBlocked}
        />
      </StyledModalContent>
    </Modal>
  );
};

MissingDocumentModal.propTypes = {
  shouldShow: PropTypes.bool,
  onClose: PropTypes.func,
  projects: PropTypes.arrayOf(
    PropTypes.shape({
      event: PropTypes.shape({
        id: PropTypes.string.isRequired,
        name: PropTypes.string.isRequired,
        endTime: PropTypes.string.isRequired,
      }),
      projectId: PropTypes.number.isRequired,
      missingDocumentCount: PropTypes.number.isRequired,
      limitDate: PropTypes.string.isRequired,
    }),
  ),
  isBlocked: PropTypes.bool,
};

export default MissingDocumentModal;
