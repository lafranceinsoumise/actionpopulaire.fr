import React from "react";
import PropTypes from "prop-types";

const InputGroup = ({ children, className = "" }) => (
  <div className={`input-group ${className}`.trim()}>{children}</div>
);

InputGroup.propTypes = {
  children: PropTypes.node,
  className: PropTypes.string,
};

InputGroup.Addon = ({ children }) => (
  <div className="input-group-addon">{children}</div>
);

InputGroup.Addon.propTypes = {
  children: PropTypes.node,
};

InputGroup.Addon.displayName = "InputGroup.Addon";

export default InputGroup;
