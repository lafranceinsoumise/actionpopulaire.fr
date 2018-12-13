import React from "react";
import classNames from "classnames";
import PropTypes from "prop-types";

const Button = props => {
  const { children, bsStyle, bsSize, type, ...otherProps } = props;
  return (
    <button
      className={classNames("btn", `btn-${bsStyle}`, bsSize && `btn-${bsSize}`)}
      type={type}
      {...otherProps}
    >
      {children}
    </button>
  );
};
Button.propTypes = {
  children: PropTypes.node,
  type: PropTypes.string,
  bsStyle: PropTypes.string,
  bsSize: PropTypes.string
};

Button.defaultProps = {
  type: "button",
  bsStyle: "default"
};

export default Button;
