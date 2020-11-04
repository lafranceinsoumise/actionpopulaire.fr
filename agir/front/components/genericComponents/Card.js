import PropTypes from "prop-types";
import style from "@agir/front/genericComponents/_variables.scss";
import styled from "styled-components";

const cardTypes = {
  default: {
    background: style.white,
    borderRadius: "0.5rem",
  },
  primary: {
    background: style.primary100,
  },
  alert: {
    background: `linear-gradient(90deg, ${style.secondary500} 0, ${style.secondary500} 3px, ${style.white} 3px)`,
    borderRadius: "0",
  },
};

const Card = styled.section`
  box-shadow: 0px 0px 3px rgba(0, 0, 0, 0.1), 0px 3px 2px rgba(0, 0, 0, 0.05);
  background: ${({ type }) =>
    type && cardTypes[type] && cardTypes[type].background
      ? cardTypes[type].background
      : cardTypes.default.background};
  padding: 1.5rem;
  border-radius: ${({ type }) =>
    type && cardTypes[type] && cardTypes[type].borderRadius
      ? cardTypes[type].borderRadius
      : cardTypes.default.borderRadius};
  font-weight: 500;

  @media (max-width: ${style.collapse}px) {
    border-radius: 0;
  }

  & p {
    font-weight: 400;

    & > strong,
    & > a {
      font-weight: bolder;
    }
    & > a {
      color: inherit;
      text-decoration: underline;
    }
  }
`;
Card.propTypes = {
  type: PropTypes.oneOf(Object.keys(cardTypes)),
};
Card.defaultProps = {
  type: "default",
};
export default Card;
