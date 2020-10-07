import style from "./style.scss";
import styled from "styled-components";
import PropTypes from "prop-types";
import { transparentize } from "polished";

const Button = styled.button`
  display: inline-block;
  padding: ${({ small }) => (small ? "8px 12px" : "12px 24px")};
  line-height: ${({ small }) => (small ? "95%" : style.lineHeightBase)}
  margin: 0;
  border: 0;
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
`;

Button.propTypes = {
  onClick: PropTypes.func,
  color: PropTypes.oneOf(["primary", "secondary", "unavailable"]),
  small: PropTypes.bool,
  disabled: PropTypes.bool,
};

Button.defaultProps = {
  small: false,
};

export default Button;
