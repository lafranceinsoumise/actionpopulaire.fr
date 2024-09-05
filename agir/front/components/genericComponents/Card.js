import isPropValid from "@emotion/is-prop-valid";
import PropTypes from "prop-types";
import styled from "styled-components";

const cardTypes = {
  default: {
    backgroundColor: "background0",
    borderRadius: 0,
  },
  primary: {
    backgroundColor: "primary100",
  },
  alert: {
    backgroundImage: `linear-gradient(90deg, transparent 0, transparent 3px, ${(props) => props.theme.background0} 3px)`,
    backgroundColor: "background0",
  },
  alert_dismissed: {
    backgroundImage: `linear-gradient(90deg, transparent 0, transparent 3px, ${(props) => props.theme.background0} 3px)`,
    backgroundColor: "background0",
  },
  error: {
    backgroundImage: `linear-gradient(90deg, transparent 0, transparent 8px, ${(props) => props.theme.background0} 8px)`,
    backgroundColor: "error500",
  },
};

const Card = styled.div
  .withConfig({
    shouldForwardProp: isPropValid,
  })
  .attrs(({ type, ...props }) => ({
    ...props,
    config: type && cardTypes[type] ? cardTypes[type] : cardTypes.default,
  }))`
  background-image: ${({ config }) => config.backgroundImage || "none"};
  background-color: ${({ config, theme }) =>
    theme[config.backgroundColor] || config.backgroundColor};
  padding: 1.5rem;
  font-weight: 500;
  cursor: ${({ onClick }) => (onClick ? "pointer" : "default")};
  border: 1px solid;
  border-color: ${(props) => props.theme.text100};
  transition:
    border-color,
    background-color 300ms;
  border-radius: ${(props) => props.theme.borderRadius};

  &:hover {
    ${({ onClick }) =>
      onClick
        ? `
      border-color: ${(props) => props.theme.text100};
    `
        : ""}
  }

  @media (max-width: ${(props) => props.theme.collapse}px) {
    padding: 1rem;
    ${(props) =>
      !props.bordered
        ? `
      border: none;
      box-shadow: ${(props) => props.theme.elaborateShadow};
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
