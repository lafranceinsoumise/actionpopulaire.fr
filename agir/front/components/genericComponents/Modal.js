import PropTypes from "prop-types";
import React from "react";
import { useTransition, animated } from "react-spring";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

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
  position: absolute;
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
  noScroll: PropTypes.bool,
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

const Modal = (props) => {
  const { shouldShow = false, children, onClose } = props;

  const transitions = useTransition(shouldShow, null, slideInTransition);

  return transitions.map(({ item, key, props }) =>
    item ? (
      <ModalFrame key={key}>
        <AnimatedOverlay onClick={onClose} shouldShow={shouldShow} />
        <ModalContent style={props}>{children}</ModalContent>
      </ModalFrame>
    ) : null
  );
};
Modal.propTypes = {
  shouldShow: PropTypes.bool,
  children: PropTypes.node,
  onClick: PropTypes.func,
};

export default Modal;
