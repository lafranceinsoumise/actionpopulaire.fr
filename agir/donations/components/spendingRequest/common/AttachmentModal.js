import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import AttachmentField from "./AttachmentField";
import SpendingRequestHelp from "./SpendingRequestHelp";
import Modal, { ModalCloseButton } from "@agir/front/genericComponents/Modal";
import { Hide } from "@agir/front/genericComponents/grid";

const StyledError = styled.div``;

const StyledModalContent = styled.div`
  position: relative;
  padding: 1.5rem;
  max-width: 600px;
  margin: 40px auto;
  background-color: white;
  border-radius: ${(props) => props.theme.borderRadius};
  display: flex;
  flex-flow: column nowrap;
  gap: 1rem;

  @media (max-width: ${(props) => props.theme.collapse}px) {
    border-radius: 0;
    max-width: 100%;
    min-height: 100vh;
    padding-top: 3rem;
    padding-bottom: 1.5rem;
    margin: 0;
    display: flex;
    flex-flow: column nowrap;
  }

  ${StyledError} {
    text-align: center;
    color: ${(props) => props.theme.redNSP};

    &:empty {
      display: none;
    }
  }
`;

const AttachmentModal = (props) => {
  const {
    shouldShow = true,
    value,
    onChange,
    onClose,
    error,
    isLoading,
  } = props;

  const globalError = error?.global || error?.detail;

  return (
    <Modal
      noScroll
      shouldShow={shouldShow}
      onClose={isLoading ? onClose : undefined}
    >
      <StyledModalContent>
        <Hide as={ModalCloseButton} onClose={onClose} disabled={isLoading} />
        <SpendingRequestHelp helpId="documentTypes" />
        <AttachmentField
          initialValue={value}
          onChange={onChange}
          resetOnChange={false}
          isLoading={isLoading}
          disabled={!shouldShow || isLoading}
          error={error}
        />
        <StyledError>{globalError}</StyledError>
      </StyledModalContent>
    </Modal>
  );
};

AttachmentModal.propTypes = {
  shouldShow: PropTypes.bool,
  value: PropTypes.object,
  onChange: PropTypes.func,
  onClose: PropTypes.func,
  error: PropTypes.oneOfType([PropTypes.string, PropTypes.object]),
  isLoading: PropTypes.bool,
};

AttachmentModal.displayName = "AttachmentModal";

export default AttachmentModal;
