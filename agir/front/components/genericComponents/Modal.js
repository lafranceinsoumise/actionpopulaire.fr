import PropTypes from "prop-types";
import React, { useCallback, useEffect, useMemo, useRef } from "react";
import { createPortal } from "react-dom";
import { useTransition, animated } from "react-spring";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";
import { useDisableBodyScroll } from "@agir/lib/utils/hooks";

const slideInTransition = {
  from: { opacity: 0, paddingTop: "2%" },
  enter: { opacity: 1, paddingTop: "0" },
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
  const transitions = useTransition(shouldShow, null, fadeInTransition);

  return transitions.map(({ item, key, props }) =>
    item ? <Overlay key={key} style={props} onClick={onClick} /> : null
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
  z-index: ${style.zindexModal};
`;

const getFocusableElements = (parent) => {
  if (!parent) {
    return [];
  }
  return [
    ...parent.querySelectorAll(
      'a[href], button, textarea, input[type="text"], input[type="radio"], input[type="checkbox"], select'
    ),
  ].filter(
    (elem) =>
      !elem.disabled &&
      !!(elem.offsetWidth || elem.offsetHeight || elem.getClientRects().length)
  );
};

const useFocusTrap = (shouldShow) => {
  const modalRef = useRef(null);
  const handleTabKey = useCallback((e) => {
    if (!modalRef.current) {
      return;
    }
    const focusableModalElements = getFocusableElements(modalRef.current);
    const firstElement = focusableModalElements[0];
    const lastElement =
      focusableModalElements[focusableModalElements.length - 1];
    if (!e.shiftKey && document.activeElement === lastElement) {
      firstElement.focus();
      e.preventDefault();
    }
    if (e.shiftKey && document.activeElement === firstElement) {
      lastElement.focus();
      e.preventDefault();
    }
  }, []);

  const keyListenersMap = useMemo(() => new Map([[9, handleTabKey]]), [
    handleTabKey,
  ]);

  useEffect(() => {
    const keyListener = (e) => {
      const listener = keyListenersMap.get(e.keyCode);
      return listener && listener(e);
    };
    if (shouldShow && modalRef.current) {
      document.addEventListener("keydown", keyListener);
      const firstElement = getFocusableElements(modalRef.current)[0];
      firstElement ? firstElement.focus() : modalRef.current.focus();
    }

    return () => document.removeEventListener("keydown", keyListener);
  }, [shouldShow, keyListenersMap]);

  return modalRef;
};

const Modal = (props) => {
  const { shouldShow = false, children, onClose, noScroll } = props;

  const modalRef = useDisableBodyScroll(noScroll, shouldShow);
  const modalContentRef = useFocusTrap(shouldShow);

  const transitions = useTransition(shouldShow, null, slideInTransition);

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
    [modalParent]
  );

  return createPortal(
    transitions.map(({ item, key, props }) =>
      item ? (
        <ModalFrame key={key} ref={modalRef}>
          <AnimatedOverlay onClick={onClose} shouldShow={shouldShow} />
          <ModalContent
            ref={modalContentRef}
            style={props}
            aria-modal="true"
            role="dialog"
          >
            {children}
          </ModalContent>
        </ModalFrame>
      ) : null
    ),
    modalParent
  );
};
Modal.propTypes = {
  shouldShow: PropTypes.bool,
  children: PropTypes.node,
  onClick: PropTypes.func,
  noScroll: PropTypes.bool,
};

export default Modal;
