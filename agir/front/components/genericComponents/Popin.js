import PropTypes from "prop-types";
import React from "react";
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
    transform: translateY(110%);
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
  const { isOpen, position = "bottom-right", children } = props;

  const popinTransition = useTransition(isOpen, null, fadeInTransition);
  const Popin = React.useMemo(() => Popins[position], [position]);

  return popinTransition.map(({ item, key, props }) =>
    item ? (
      <Popin key={key} style={props}>
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
