import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

import BottomSheet from "@agir/front/genericComponents/BottomSheet";
import Button from "@agir/front/genericComponents/Button";
import Modal from "@agir/front/genericComponents/Modal";
import Spacer from "@agir/front/genericComponents/Spacer";
import { ResponsiveLayout } from "@agir/front/genericComponents/grid";

const ModalContainer = styled.div`
  background: white;
  width: 40%;
  max-width: 500px;
  margin: 5% auto;
  border-radius: ${style.borderRadius};
  display: flex;
  justify-content: center;

  @media (max-width: ${style.collapse}px) {
    width: 100%;
    max-width: unset;
    margin: 0;
  }
`;

const ModalContent = styled.div`
  display: inline-flex;
  flex-direction: column;
  padding: 1rem 1.5rem;

  h3 {
    font-size: 1rem;
  }

  & > ${Button} {
    margin-bottom: 1rem;
    color: white;

    &:hover,
    &:focus {
      color: white;
    }
  }
`;

const ModalConfirmation = (props) => {
  const {
    shouldShow = false,
    onClose,
    title,
    children,
    dismissLabel,
    confirmationLabel = "",
    confirmationUrl = "",
    onConfirm = null,
    shouldDismissOnClick = true,
    isConfirming = false,
    disabled = false,
  } = props;

  return (
    <ResponsiveLayout
      DesktopLayout={Modal}
      MobileLayout={BottomSheet}
      shouldShow={shouldShow}
      isOpen={shouldShow}
      onClose={onClose}
      onDismiss={onClose}
      shouldDismissOnClick={shouldDismissOnClick}
      noScroll
    >
      <ModalContainer>
        <ModalContent>
          <h3>{title}</h3>
          {children}
          <Spacer size="1rem" />
          {!!confirmationUrl && (
            <Button
              wrap
              color="primary"
              type="button"
              link
              route={confirmationUrl}
              disabled={disabled || isConfirming}
              loading={isConfirming}
            >
              {confirmationLabel}
            </Button>
          )}
          {!!onConfirm && (
            <Button
              wrap
              color="primary"
              type="button"
              onClick={onConfirm}
              disabled={disabled || isConfirming}
              loading={isConfirming}
            >
              {confirmationLabel}
            </Button>
          )}
          {dismissLabel && (
            <Button
              wrap
              type="button"
              onClick={onClose}
              style={{ color: style.black1000 }}
              disabled={isConfirming}
            >
              {dismissLabel}
            </Button>
          )}
        </ModalContent>
      </ModalContainer>
    </ResponsiveLayout>
  );
};

ModalConfirmation.propTypes = {
  shouldShow: PropTypes.bool,
  onClose: PropTypes.func,
  title: PropTypes.node,
  children: PropTypes.node,
  dismissLabel: PropTypes.node,
  confirmationLabel: PropTypes.node,
  confirmationUrl: PropTypes.string,
  onConfirm: PropTypes.func,
  shouldDismissOnClick: PropTypes.bool,
  isConfirming: PropTypes.bool,
  disabled: PropTypes.bool,
};

export default ModalConfirmation;
