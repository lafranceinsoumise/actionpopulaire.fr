import PropTypes from "prop-types";
import React, { useCallback, useEffect, useMemo, useRef } from "react";
import { useTransition, animated } from "@react-spring/web";
import { useKeyPressEvent } from "react-use";
import styled from "styled-components";

import { useFocusTrap } from "@agir/lib/utils/hooks";

const fadeInTransition = {
  from: { opacity: 0 },
  enter: { opacity: 1 },
  leave: { opacity: 0 },
  delay: 200,
};

const BasePopin = styled(animated.div)`
  isolation: isolate;
  position: absolute;
  z-index: 1;
  width: max-content;
  height: auto;
  padding: 1rem;
  background-color: ${(props) => props.theme.white};
  box-shadow: ${(props) => props.theme.cardShadow};
  border-radius: ${(props) => props.theme.borderRadius};

  & > * {
    margin: 0;
  }
`;

const Popins = {
  "bottom-right": styled(BasePopin)`
    right: 0;
    bottom: -${(props) => props.$gap};
    transform: translateY(100%);
  `,
  bottom: styled(BasePopin)`
    left: 0;
    right: 0;
    bottom: -${(props) => props.$gap};
    width: 100%;
    transform: translateY(100%);
  `,
  right: styled(BasePopin)`
    left: 100%;
    transform: translateX(${(props) => props.$gap});
    top: 0;
  `,
};

export const PopinContainer = (props) => {
  const {
    isOpen,
    onDismiss,
    position = "bottom-right",
    gap = "0.5rem",
    shouldDismissOnClick = false,
    children,
  } = props;

  const popinRef = useFocusTrap(isOpen);
  const popinTransition = useTransition(isOpen, fadeInTransition);
  const Popin = useMemo(() => Popins[position], [position]);

  const closeOnClickOutside = useCallback(
    (event) => {
      popinRef.current &&
        !popinRef.current.contains(event.target) &&
        onDismiss &&
        onDismiss();
    },
    [onDismiss],
  );

  useKeyPressEvent("Escape", onDismiss);

  useEffect(() => {
    if (typeof window !== "undefined") {
      isOpen && document.addEventListener("click", closeOnClickOutside);
      return () => {
        document.removeEventListener("click", closeOnClickOutside);
      };
    }
  }, [isOpen, closeOnClickOutside]);

  return popinTransition((style, item) =>
    item ? (
      <Popin
        ref={popinRef}
        style={style}
        $gap={gap}
        onClick={shouldDismissOnClick ? onDismiss : undefined}
      >
        {children}
      </Popin>
    ) : null,
  );
};
PopinContainer.propTypes = {
  isOpen: PropTypes.bool.isRequired,
  onDismiss: PropTypes.func,
  position: PropTypes.oneOf(Object.keys(Popins)),
  gap: PropTypes.string,
  shouldDismissOnClick: PropTypes.bool,
  children: PropTypes.node,
};

export default PopinContainer;
