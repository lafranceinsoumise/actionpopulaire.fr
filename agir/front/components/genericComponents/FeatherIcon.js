import React from "react";
import PropTypes from "prop-types";
import styled from "styled-components";
import { icons } from "feather-icons";

import mainStyle from "./style.scss";

export const allIcons = Object.keys(icons);

export const RawFeatherIcon = styled.div.attrs(
  ({ name, color, strokeWidth, strokeLinecap, strokeLinejoin, svgStyle }) => {
    const attrs = {
      name,
      color,
      "stroke-width": strokeWidth,
      "stroke-linecap": strokeLinecap,
      "stroke-linejoin": strokeLinejoin,
    };
    Object.keys(attrs).map((k) => attrs[k] === undefined && delete attrs[k]);

    if (svgStyle !== undefined) {
      attrs.style = Object.keys(svgStyle)
        .map((key) => {
          const cssKey = key.replace(/[A-Z]/g, (m) => `-${m.toLowerCase()}`);
          return `${cssKey}:${svgStyle[key]}`;
        })
        .join(";");
    }

    return {
      dangerouslySetInnerHTML: { __html: icons[name].toSvg(attrs) },
    };
  }
)`
  display: inline-flex;
  align-items: center;

  svg {
    position: relative;
    width: ${(props) => props.width};
    height: ${(props) => props.height};
    top: ${(props) => props.top};
  }
`;

RawFeatherIcon.propTypes = {
  name: PropTypes.oneOf(allIcons),
  color: PropTypes.string,
  width: PropTypes.string,
  height: PropTypes.string,
  strokeWidth: PropTypes.number,
  strokeLinecap: PropTypes.number,
  strokeLinejoin: PropTypes.number,
  style: PropTypes.objectOf(PropTypes.string),
};

/*
La taille de police de base est de 16 pixels.
Les grands icônes doivent faire 24 pixels (1.5rem)
Les petits icônes doivent faire 16 pixels (1rem)
 */

const FeatherIcon = ({ name, type, color, inline }) => {
  // stroke dimensions
  const strokeWidth = type === "normal" ? 2 : 1.33;

  // positionning dimensions
  const dimension = type === "normal" ? "1.5rem" : "1rem";

  const top = inline ? (type === "normal" ? "0.3rem" : "0.15rem") : "0";

  // color
  color = color || (type === "normal" ? mainStyle.brandBlack : mainStyle.gray);

  return (
    <RawFeatherIcon
      name={name}
      width={dimension}
      height={dimension}
      color={color}
      top={top}
      strokeWidth={strokeWidth}
    />
  );
};
FeatherIcon.propTypes = {
  name: PropTypes.oneOf(allIcons),
  type: PropTypes.oneOf(["normal", "small"]),
  color: PropTypes.string,
  inline: PropTypes.bool,
};

FeatherIcon.defaultProps = {
  type: "normal",
  inline: false,
};

FeatherIcon.RawFeatherIcon = RawFeatherIcon;
FeatherIcon.allIcons = allIcons;

export default FeatherIcon;
