import PropTypes from "prop-types";
import style from "./style.scss";
import styled from "styled-components";

const cardTypes = {
  default: {
    background: style.white,
  },
  primary: {
    background: style.primary100,
  },
};

const Card = styled.section`
  box-shadow: 0px 0px 3px rgba(0, 0, 0, 0.1), 0px 3px 2px rgba(0, 0, 0, 0.05);
  background: ${({ type }) =>
    type && cardTypes[type] && cardTypes[type].background
      ? cardTypes[type].background
      : cardTypes.default.background};
  padding: 1.5rem;
  border-radius: 0.5rem;
  font-weight: 500;

  & p {
    font-weight: 400;
  }
`;
Card.propTypes = {
  type: PropTypes.oneOf(Object.keys(cardTypes)),
};
Card.defaultProps = {
  type: "default",
};
export default Card;
