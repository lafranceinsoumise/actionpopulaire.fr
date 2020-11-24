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

const Card = styled.div`
  box-shadow: ${style.elaborateShadow};
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
  cursor: ${({ onClick }) => (onClick ? "pointer" : "default")};

  @media (max-width: ${style.collapse}px) {
    border-radius: 0;
    padding: 1rem;
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
