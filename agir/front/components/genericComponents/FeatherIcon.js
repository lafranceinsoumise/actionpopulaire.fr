import React from "react";
import PropTypes from "prop-types";
import { icons } from "feather-icons";

import style from "./style.scss";

export const allIcons = Object.keys(icons);

export const RawFeatherIcon = ({
  name,
  color,
  width,
  height,
  strokeWidth,
  strokeLinecap,
  strokeLinejoin,
}) => {
  const attrs = {
    name,
    color,
    width,
    height,
    "stroke-width": strokeWidth,
    "stroke-linecap": strokeLinecap,
    "stroke-linejoin": strokeLinejoin,
  };

  Object.keys(attrs).map((k) => attrs[k] === undefined && delete attrs[k]);

  return (
    <div
      dangerouslySetInnerHTML={{
        __html: icons[name].toSvg(attrs),
      }}
    />
  );
};
RawFeatherIcon.propTypes = {
  name: PropTypes.oneOf(allIcons),
  color: PropTypes.string,
  width: PropTypes.number,
  height: PropTypes.number,
  strokeWidth: PropTypes.number,
  strokeLinecap: PropTypes.number,
  strokeLinejoin: PropTypes.number,
};

const FeatherIcon = ({ name, type }) => {
  const dimension = type === "normal" ? 24 : 16;
  const color = type === "normal" ? style.brandBlack : style.gray;
  const strokeWidth = type === "normal" ? 2 : 1.33;

  return (
    <RawFeatherIcon
      name={name}
      width={dimension}
      height={dimension}
      color={color}
      strokeWidth={strokeWidth}
    />
  );
};
FeatherIcon.propTypes = {
  name: PropTypes.oneOf(allIcons),
  type: PropTypes.oneOf(["normal", "small"]),
};

FeatherIcon.defaultProps = {
  type: "normal",
};

export default FeatherIcon;
