import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import AttachmentField from "./AttachmentField";
import SpendingRequestHelp from "./SpendingRequestHelp";
import Modal, { ModalCloseButton } from "@agir/front/genericComponents/Modal";
import { Hide } from "@agir/front/genericComponents/grid";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";

const StyledError = styled.div``;
const StyledCloseButton = styled(ModalCloseButton).attrs((props) => ({
  ...props,
  size: "1.5rem",
}))`
  top: 1rem;
  right: 1rem;
`;
const StyledWarning = styled.div`
  display: flex;
  flex-flow: row nowrap;
  align-items: center;
  padding: 1rem;
  gap: 1rem;
  font-size: 0.875rem;
  line-height: 1.5;
  margin: 0 0 0.5rem;
  background-color: ${(props) => props.theme.redNSP + "44"};
  border-radius: ${(props) => props.theme.borderRadius};

  ${RawFeatherIcon} {
    flex: 0 0 auto;
    color: currentcolor;
  }
`;

const StyledModalContent = styled.div`
  position: relative;
  padding: 2rem 2rem 1.5rem;
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
    padding: 3.5rem 1rem 1.5rem;
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

  footer {
    @media (min-width: ${(props) => props.theme.collapse}px) {
      justify-content: space-between;
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
    warning,
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
        <Hide as={StyledCloseButton} onClose={onClose} disabled={isLoading} />
        <SpendingRequestHelp helpId="documentTypes" />
        {warning && (
          <StyledWarning>
            <RawFeatherIcon name="alert-circle" />
            {warning}
          </StyledWarning>
        )}
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
  warning: PropTypes.string,
  isLoading: PropTypes.bool,
};

AttachmentModal.displayName = "AttachmentModal";

export default AttachmentModal;
