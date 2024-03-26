import PropTypes from "prop-types";
import React, { useCallback, useEffect, useMemo, useRef } from "react";
import { createPortal } from "react-dom";
import { useTransition, animated } from "@react-spring/web";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";
import { useDisableBodyScroll } from "@agir/lib/utils/hooks";
import { useDownloadBanner } from "@agir/front/app/hooks.js";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";

const springConfig = {
  tension: 160,
  friction: 30,
};

const slideInTransitions = {
  right: {
    config: springConfig,
    from: { right: 0, transform: "translateX(100%)" },
    enter: { transform: "translateX(0%)" },
    leave: { transform: "translateX(100%)" },
  },
  left: {
    config: springConfig,
    from: { left: 0, transform: "translateX(-100%)" },
    enter: { transform: "translateX(0%)" },
    leave: { transform: "translateX(-100%)" },
  },
};

const fadeInTransition = {
  config: springConfig,
  from: { opacity: 0 },
  enter: { opacity: 1 },
  leave: { opacity: 0 },
};

const Overlay = styled(animated.div)`
  width: 100%;
  height: 100%;
  max-height: 100%;
  position: fixed;
  top: 0;
  bottom: 0;
  left: 0;
  right: 0;
  background-color: rgba(164, 159, 173, 0.6);
  cursor: ${({ onClick }) => (onClick ? "pointer" : "default")};
  z-index: 1;
  will-change: opacity;
`;

const AnimatedOverlay = (props) => {
  const { shouldShow = false, onClick } = props;
  const transitions = useTransition(!!shouldShow, fadeInTransition);

  return transitions((style, item) =>
    item ? <Overlay style={style} onClick={onClick} /> : null,
  );
};

AnimatedOverlay.propTypes = {
  shouldShow: PropTypes.bool,
  onClick: PropTypes.func,
  className: PropTypes.string,
};

export const StyledBackButton = styled.button`
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
  position: fixed;
  z-index: ${style.zindexPanel};
  height: 100%;
  max-height: -webkit-fill-available;
  overflow: auto;
  top: 0;
  ${({ $position }) => `${$position}: 0;`}
  display: inline-block;
  width: auto;
  min-width: 600px;
  background-color: white;
  margin: 0;
  padding: 2rem 1.5rem;
  will-change: transform;

  @media (max-width: ${style.collapse}px) {
    display: block;
    width: 100%;
    min-width: 100%;
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
  height: 100vh;
  max-height: -webkit-fill-available;
  overflow: hidden;
  z-index: ${style.zindexPanel};
  pointer-events: ${({ $open }) => ($open ? "auto" : "none")};

  @media (max-width: ${style.collapse}px) {
    display: block;
    width: 100%;
    min-width: 100%;
    z-index: ${({ $isBehindTopBar }) =>
      $isBehindTopBar ? style.zindexTopBar - 1 : style.zindexPanel};

    ${PanelContent} {
      padding-top: ${({ $isBehindTopBar, $hasDownloadBanner }) => {
        if ($isBehindTopBar && $hasDownloadBanner) {
          return "136px";
        }
        if ($isBehindTopBar) {
          return "56px";
        }
        return "1.5rem";
      }};
    }
  }
`;

const getFocusableElements = (parent) => {
  if (!parent) {
    return [];
  }
  return [
    ...parent.querySelectorAll(
      'a[href], button, textarea, input[type="text"], input[type="radio"], input[type="checkbox"], select',
    ),
  ].filter(
    (elem) =>
      !elem.disabled &&
      !!(elem.offsetWidth || elem.offsetHeight || elem.getClientRects().length),
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

  const keyListenersMap = useMemo(
    () => new Map([[9, handleTabKey]]),
    [handleTabKey],
  );

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
    isBehindTopBar,
    className,
    style,
  } = props;

  const [hasDownloadBanner] = useDownloadBanner();

  const panelRef = useDisableBodyScroll(noScroll, shouldShow);
  const panelContentRef = useFocusTrap(shouldShow);

  const slideInTransition =
    slideInTransitions[position] || slideInTransitions.right;
  const transitions = useTransition(!!shouldShow, slideInTransition);

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
    [panelParent],
  );

  return createPortal(
    <PanelFrame
      ref={panelRef}
      $open={shouldShow}
      $isBehindTopBar={isBehindTopBar}
      $hasDownloadBanner={hasDownloadBanner}
    >
      <AnimatedOverlay onClick={onClose} shouldShow={shouldShow} />
      {transitions((tStyle, item) =>
        item ? (
          <PanelContent
            ref={panelContentRef}
            className={className}
            style={{ ...style, ...tStyle }}
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
        ) : null,
      )}
    </PanelFrame>,
    panelParent,
  );
};
Panel.propTypes = {
  shouldShow: PropTypes.bool,
  children: PropTypes.node,
  onClose: PropTypes.func,
  onBack: PropTypes.func,
  noScroll: PropTypes.bool,
  isBehindTopBar: PropTypes.bool,
  position: PropTypes.oneOf(["right", "left"]),
  title: PropTypes.string,
  className: PropTypes.string,
};

export default Panel;
