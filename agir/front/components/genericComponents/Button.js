import style from "./style.scss";
import styled from "styled-components";
import PropTypes from "prop-types";
import { transparentize } from "polished";
import { icons } from "feather-icons";

const Button = styled.button`
  display: inline-block;
  padding: ${({ small }) => (small ? "8px 12px" : "12px 24px")};
  line-height: ${({ small }) => (small ? "95%" : style.lineHeightBase)}
  margin: 0;
  border: 0;
  border-radius: 8px;
  min-height: ${({ small }) => (small ? "32px" : "48px")};
  text-align: center;
  text-transform: uppercase;
  font-weight: 700;
  font-size: ${({ small }) => (small ? "11px" : "14px")};

  ${({ color, disabled }) => {
    let background,
      hoverBackground,
      labelColor,
      border = false;

    if (color === "primary") {
      background = style.brandPrimary;
      hoverBackground = style.brandPrimaryDark;
      labelColor = "#fff";
    } else if (color === "secondary") {
      background = style.brandSecondary;
      hoverBackground = style.brandSecondaryDark;
      labelColor = "#fff";
    } else if (color === "confirmed") {
      background = style.brandPrimaryLight;
      hoverBackground = style.brandPrimaryLightHover;
      labelColor = style.brandPrimary;
    } else if (color === "unavailable") {
      background = "#fff";
      hoverBackground = "#fff";
      labelColor = style.gray;
      border = style.grayLight;
    } else {
      background = style.grayLighter;
      hoverBackground = style.grayLight;
      labelColor = style.textColor;
    }

    if (disabled) {
      background = transparentize(0.7, background);
      labelColor = transparentize(0.3, labelColor);
    }

    let result = `
      background-color: ${background};
      color: ${labelColor};

      &:hover {
        color: ${labelColor};
        text-decoration: none;
      }
    `;

    if (border) {
      result += `border: 1px solid ${border};`;
    }

    if (disabled) {
      result += `cursor: not-allowed;`;
    } else {
      result += `
        &:hover {
          background-color: ${hoverBackground};
        }
      `;
    }

    return result;
  }}

  ${({ icon, small }) =>
    icon
      ? `
    &:before {
      content: url('data:image/svg+xml;utf8,${icons[icon].toSvg({
        height: small ? 11 : 16,
        width: small ? 11 : 16,
      })}');
      position: relative;
      top: 0.15rem;
      margin-right: ${small ? "4px" : "8px"};
    }
  `
      : ""}
}}
`;

Button.colors = ["primary", "secondary", "confirmed", "unavailable"];

Button.propTypes = {
  onClick: PropTypes.func,
  color: PropTypes.oneOf(Button.colors),
  small: PropTypes.bool,
  disabled: PropTypes.bool,
  href: PropTypes.string,
};

Button.defaultProps = {
  small: false,
};

export default Button;
