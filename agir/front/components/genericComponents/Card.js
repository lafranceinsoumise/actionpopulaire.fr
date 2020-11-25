import PropTypes from "prop-types";
import style from "@agir/front/genericComponents/_variables.scss";
import styled from "styled-components";

const cardTypes = {
  default: {
    background: style.white,
    borderRadius: style.defaultBorderRadius,
  },
  primary: {
    background: style.primary100,
  },
  alert: {
    background: `linear-gradient(90deg, ${style.black1000} 0, ${style.black1000} 3px, ${style.white} 3px)`,
  },
};

const Card = styled.div`
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
  border: 1px solid ${style.black100};

  @media (max-width: ${style.collapse}px) {
    border: none;
    box-shadow: ${style.elaborateShadow};
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
