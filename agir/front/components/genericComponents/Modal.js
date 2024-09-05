import PropTypes from "prop-types";
import React, { useEffect, useMemo } from "react";
import { createPortal } from "react-dom";
import { useTransition, animated } from "@react-spring/web";
import styled from "styled-components";

import { useDisableBodyScroll, useFocusTrap } from "@agir/lib/utils/hooks";
import { RawFeatherIcon } from "./FeatherIcon";

const slideInTransition = {
  from: { opacity: 0, paddingTop: "2%" },
  enter: { opacity: 1, paddingTop: "0%" },
  leave: { opacity: 0, paddingTop: "2%" },
};

const fadeInTransition = {
  from: { opacity: 0 },
  enter: { opacity: 1 },
  leave: { opacity: 0 },
};

const Overlay = styled(animated.div)`
  width: 100%;
  height: 100%;
  position: fixed;
  top: 0;
  bottom: 0;
  left: 0;
  right: 0;
  background-color: rgba(164, 159, 173, 0.6);
  cursor: ${({ onClick }) => (onClick ? "pointer" : "default")};
  z-index: 1;
`;

const AnimatedOverlay = (props) => {
  const { shouldShow = false, onClick } = props;
  const transitions = useTransition(shouldShow, fadeInTransition);

  return transitions((style, item) =>
    item ? <Overlay style={style} onClick={onClick} /> : null,
  );
};

AnimatedOverlay.propTypes = {
  shouldShow: PropTypes.bool,
  onClick: PropTypes.func,
  className: PropTypes.string,
};

const ModalContent = styled(animated.div)`
  position: absolute;
  top: 0;
  left: 50%;
  transform: translate3d(-50%, 0, 0);
  z-index: 2;
  width: 100%;
  height: 100%;
  margin: 0 auto;
  pointer-events: none;

  & > * {
    pointer-events: all;
  }
`;

const ModalFrame = styled.div`
  position: fixed;
  top: 0;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 0;
  margin: 0;
  width: 100vw;
  min-height: 100vh;
  overflow-x: hidden;
  overflow-y: auto;
  z-index: ${(props) => props.theme.zindexModal};
`;

const StyledCloseButton = styled.button`
  position: absolute;
  top: 1rem;
  right: 1rem;
  padding: 0;
  color: ${(props) => props.theme.text700};
  z-index: 1;
  background-color: transparent;
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
`;

export const ModalCloseButton = ({ onClose, size = "2rem", ...rest }) => {
  if (!onClose) {
    return null;
  }

  return (
    <StyledCloseButton
      {...rest}
      onClick={onClose}
      aria-label="Fermer la modale"
    >
      <RawFeatherIcon name="x" width={size} height={size} />
    </StyledCloseButton>
  );
};

ModalCloseButton.propTypes = {
  onClose: PropTypes.func,
  size: PropTypes.string,
};

const Modal = (props) => {
  const { shouldShow = false, children, onClose, noScroll, className } = props;

  const modalRef = useDisableBodyScroll(noScroll, shouldShow);
  const modalContentRef = useFocusTrap(shouldShow);

  const transitions = useTransition(shouldShow, slideInTransition);

  const modalParent = useMemo(() => {
    const modalParent = document.createElement("div");
    modalParent.className = "modal-root";
    document.body.appendChild(modalParent);

    return modalParent;
  }, []);

  useEffect(
    () => () => {
      modalParent && document.body.removeChild(modalParent);
    },
    [modalParent],
  );

  return createPortal(
    transitions((style, item) =>
      item ? (
        <ModalFrame ref={modalRef} className={className}>
          <AnimatedOverlay onClick={onClose} shouldShow={shouldShow} />
          <ModalContent
            ref={modalContentRef}
            style={style}
            aria-modal="true"
            role="dialog"
          >
            {children}
          </ModalContent>
        </ModalFrame>
      ) : null,
    ),
    modalParent,
  );
};
Modal.propTypes = {
  shouldShow: PropTypes.bool,
  children: PropTypes.node,
  onClose: PropTypes.func,
  noScroll: PropTypes.bool,
};

export default Modal;
