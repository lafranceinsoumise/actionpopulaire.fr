import PropTypes from "prop-types";
import React, { useCallback, useEffect, useMemo, useRef } from "react";
import { createPortal } from "react-dom";
import { useTransition, animated } from "react-spring";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";
import { useDisableBodyScroll } from "@agir/lib/utils/hooks";

import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";

const slideInTransitions = {
  right: {
    from: { right: "-100%" },
    enter: { right: "0" },
    leave: { right: "-100%" },
  },
  left: {
    from: { left: "-100%" },
    enter: { left: "0" },
    leave: { left: "-100%" },
  },
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

const StyledBackButton = styled.button`
  &,
  &:hover,
  &:focus {
    background-color: transparent;
    border: none;
    box-shadow: none;
    padding: 0 0 0.5rem;
    margin: 0;
    text-align: left;
    cursor: pointer;
  }
  &:hover,
  &:focus {
    opacity: 0.75;
  }
`;

const PanelContent = styled(animated.aside)`
  position: absolute;
  top: 0;
  ${({ $position }) => `${$position}: 0;`}
  z-index: 2;
  width: 400px;
  min-height: 100%;
  background-color: white;
  margin: 0;
  padding: 2rem 1.5rem;

  @media (max-width: ${style.collapse}px) {
    width: 100%;
    padding: 1.5rem;
  }

  & > h4 {
    margin: 0;
    padding: 0 0 0.5rem;
  }
`;

const PanelFrame = styled.div`
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
  z-index: ${style.zindexPanel};
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
  const panelRef = useRef(null);
  const handleTabKey = useCallback((e) => {
    if (!panelRef.current) {
      return;
    }
    const focusablePanelElements = getFocusableElements(panelRef.current);
    const firstElement = focusablePanelElements[0];
    const lastElement =
      focusablePanelElements[focusablePanelElements.length - 1];
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
    if (shouldShow && panelRef.current) {
      document.addEventListener("keydown", keyListener);
      const firstElement = getFocusableElements(panelRef.current)[0];
      firstElement ? firstElement.focus() : panelRef.current.focus();
    }

    return () => document.removeEventListener("keydown", keyListener);
  }, [shouldShow, keyListenersMap]);

  return panelRef;
};

const Panel = (props) => {
  const {
    shouldShow = false,
    position = "right",
    title,
    children,
    onClose,
    onBack,
    noScroll,
  } = props;

  const panelRef = useDisableBodyScroll(noScroll, shouldShow);
  const panelContentRef = useFocusTrap(shouldShow);

  const slideInTransition =
    slideInTransitions[position] || slideInTransitions.right;
  const transitions = useTransition(shouldShow, null, slideInTransition);

  const panelParent = useMemo(() => {
    const panelParent = document.createElement("div");
    panelParent.className = "panel-root";
    document.body.appendChild(panelParent);

    return panelParent;
  }, []);

  useEffect(
    () => () => {
      panelParent && document.body.removeChild(panelParent);
    },
    [panelParent]
  );

  return createPortal(
    transitions.map(({ item, key, props }) =>
      item ? (
        <PanelFrame key={key} ref={panelRef}>
          <AnimatedOverlay onClick={onClose} shouldShow={shouldShow} />
          <PanelContent
            ref={panelContentRef}
            style={props}
            aria-panel="true"
            role="dialog"
            $position={position}
          >
            {typeof onBack === "function" ? (
              <StyledBackButton type="button" onClick={onBack}>
                <RawFeatherIcon
                  name="arrow-left"
                  aria-label="Retour"
                  width="1.5rem"
                  height="1.5rem"
                />
              </StyledBackButton>
            ) : null}
            {title && <h4>{title}</h4>}
            {children}
          </PanelContent>
        </PanelFrame>
      ) : null
    ),
    panelParent
  );
};
Panel.propTypes = {
  shouldShow: PropTypes.bool,
  children: PropTypes.node,
  onClose: PropTypes.func,
  noScroll: PropTypes.bool,
};

export default Panel;
