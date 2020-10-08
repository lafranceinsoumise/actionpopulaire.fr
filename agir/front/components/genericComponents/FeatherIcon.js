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
    top: ${(props) => props.vOffset || 0};

    width: ${(props) => props.width};
    height: ${(props) => props.height};
  }
`;

RawFeatherIcon.propTypes = {
  name: PropTypes.oneOf(allIcons),
  color: PropTypes.string,
  width: PropTypes.number,
  height: PropTypes.number,
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

const FeatherIcon = ({ name, type, color }) => {
  // stroke dimensions
  const strokeWidth = type === "normal" ? 2 : 1.33;

  // positionning dimensions
  const remDimension = type === "normal" ? 1.5 : 1;
  const topValue = type === "normal" ? 0.3 : 0.175;

  // color
  color = color || (type === "normal" ? mainStyle.brandBlack : mainStyle.gray);

  return (
    <RawFeatherIcon
      name={name}
      width={`${remDimension}rem`}
      height={`${remDimension}rem`}
      color={color}
      strokeWidth={strokeWidth}
      vOffset={`${topValue}rem`}
    />
  );
};
FeatherIcon.propTypes = {
  name: PropTypes.oneOf(allIcons),
  type: PropTypes.oneOf(["normal", "small"]),
  color: PropTypes.string,
};

FeatherIcon.defaultProps = {
  type: "normal",
};

FeatherIcon.RawFeatherIcon = RawFeatherIcon;
FeatherIcon.allIcons = allIcons;

export default FeatherIcon;
