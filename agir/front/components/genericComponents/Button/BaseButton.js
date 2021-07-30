import PropTypes from "prop-types";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

import Link from "@agir/front/app/Link";

import { ICONS, getIconDataUrl } from "./utils";

export const BaseButton = styled.button
  .withConfig({
    shouldForwardProp: (prop) =>
      ["link", "small", "block", "wrap"].includes(prop) === false,
  })
  .attrs(({ link, as, ...rest }) => ({
    ...rest,
    as: link ? Link : as,
  }))`
  margin: 0;
  justify-content: center;
  align-items: center;
  text-align: center;
  font-weight: 500;
  border: 1px solid;
  cursor: pointer;

  white-space: ${({ wrap }) => (wrap ? "normal" : "nowrap")};
  text-overflow: ${({ wrap }) => (wrap ? "inherit" : "ellipsis")};
  overflow: ${({ wrap }) => (wrap ? "auto" : "hidden")};

  display: ${({ block }) => (block ? "flex" : "inline-flex")};
  width: ${({ block }) => (block ? "100%" : "auto")};

  padding: ${({ small }) => (small ? "0.5rem 0.75rem" : "0.75rem 1.5rem")};
  line-height: ${({ small }) => (small ? "1" : "1.5")};
  font-size: ${({ small }) => (small ? "0.875rem" : "1rem")};

  border-radius: ${style.borderRadius};

  background-color: ${style.black50};
  border-color: ${style.black50};
  color: ${style.black1000};

  &:hover,
  &:focus,
  &:active {
    text-decoration: none;
  }

  &[disabled],
  &[disabled]:hover,
  &[disabled]:focus,
  &[disabled]:active {
    cursor: not-allowed;
  }

  &:before {
    flex: 0 0 auto;
    background-image: ${getIconDataUrl({ color: style.black1000 })};
    content: "";
    height: 1rem;
    width: 1rem;
    background-size: contain;
    background-repeat: no-repeat;
    background-position: center center;
    margin-right: ${({ small }) => (small ? "0.375rem" : "0.5rem")};
    display: ${({ icon }) => (icon && ICONS[icon] ? "inline-block" : "none")};
  }

  & > * {
    flex: 0 0 auto;
  }
}}
`;

BaseButton.propTypes = {
  link: PropTypes.bool,
  disabled: PropTypes.bool,
  small: PropTypes.bool,
  block: PropTypes.bool,
  wrap: PropTypes.bool,
  icon: PropTypes.string,
};
BaseButton.defaultProps = {
  link: false,
  disabled: false,
  small: false,
  block: false,
  wrap: false,
};

export default BaseButton;
