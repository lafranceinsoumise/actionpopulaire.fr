import isPropValid from "@emotion/is-prop-valid";
import PropTypes from "prop-types";
import style from "@agir/front/genericComponents/_variables.scss";
import styled from "styled-components";

const cardTypes = {
  default: {
    background: style.white,
    borderRadius: 0,
  },
  primary: {
    background: style.primary100,
  },
  alert: {
    backgroundImage: `linear-gradient(90deg, transparent 0, transparent 3px, ${style.white} 3px)`,
    backgroundColor: style.black1000,
  },
  alert_dismissed: {
    backgroundImage: `linear-gradient(90deg, transparent 0, transparent 3px, ${style.white} 3px)`,
    backgroundColor: style.white,
  },
};

const Card = styled.div.withConfig({
  shouldForwardProp: isPropValid,
})`
  background: ${({ type }) =>
    type && cardTypes[type] && cardTypes[type].background
      ? cardTypes[type].background
      : cardTypes.default.background};
  background-image: ${({ type }) =>
    type && cardTypes[type] && cardTypes[type].backgroundImage
      ? cardTypes[type].backgroundImage
      : "none"};
  background-color: ${({ type }) =>
    type && cardTypes[type] && cardTypes[type].backgroundColor
      ? cardTypes[type].backgroundColor
      : cardTypes.default.background};
  padding: 1.5rem;
  font-weight: 500;
  cursor: ${({ onClick }) => (onClick ? "pointer" : "default")};
  border: 1px solid;
  border-color: ${style.black100};
  transition:
    border-color,
    background-color 300ms;
  border-radius: ${style.borderRadius};

  &:hover {
    ${({ onClick }) =>
      onClick
        ? `
      border-color: ${style.black100};
    `
        : ""}
  }

  @media (max-width: ${style.collapse}px) {
    padding: 1rem;
    ${(props) =>
      !props.bordered
        ? `
      border: none;
      box-shadow: ${style.elaborateShadow};
      border-radius: 0;
    `
        : ""}
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
