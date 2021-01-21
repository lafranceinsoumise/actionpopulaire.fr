import PropTypes from "prop-types";
import React, { useCallback, useEffect, useMemo, useRef } from "react";
import { useTransition, animated } from "react-spring";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

const fadeInTransition = {
  from: { opacity: 0 },
  enter: { opacity: 1 },
  leave: { opacity: 0 },
  delay: 200,
};

const BasePopin = styled(animated.div)`
  position: absolute;
  z-index: 1;
  width: 250px;
  padding: 1rem;
  background-color: ${style.white};
  border: 1px solid ${style.black200};
  box-shadow: 0px 3px 2px rgba(0, 35, 44, 0.05);
`;

const Popins = {
  "bottom-right": styled(BasePopin)`
    right: 0;
    bottom: 0;
    transform: translateY(100%);
  `,
  bottom: styled(BasePopin)`
    left: 0;
    right: 0;
    bottom: 0;
    width: 100%;
    transform: translateY(100%);
  `,
};

export const PopinContainer = (props) => {
  const { isOpen, onDismiss, position = "bottom-right", children } = props;

  const popinRef = useRef();
  const popinTransition = useTransition(isOpen, null, fadeInTransition);
  const Popin = useMemo(() => Popins[position], [position]);

  const closeOnClickOutside = useCallback(
    (event) => {
      popinRef.current &&
        !popinRef.current.contains(event.target) &&
        onDismiss &&
        onDismiss();
    },
    [onDismiss]
  );
  useEffect(() => {
    if (typeof window !== "undefined") {
      isOpen && document.addEventListener("click", closeOnClickOutside);
      return () => {
        document.removeEventListener("click", closeOnClickOutside);
      };
    }
  }, [isOpen, closeOnClickOutside]);

  return popinTransition.map(({ item, key, props }) =>
    item ? (
      <Popin ref={popinRef} key={key} style={props}>
        {children}
      </Popin>
    ) : null
  );
};
PopinContainer.propTypes = {
  isOpen: PropTypes.bool.isRequired,
  onDismiss: PropTypes.func,
  position: PropTypes.oneOf(Object.keys(Popins)),
  children: PropTypes.node,
};

export default PopinContainer;
