import React from "react";
import PropTypes from "prop-types";

const InputGroup = ({ children }) => (
  <div className="input-group">{children}</div>
);

InputGroup.propTypes = {
  children: PropTypes.node,
};

InputGroup.Addon = ({ children }) => (
  <div className="input-group-addon">{children}</div>
);

InputGroup.Addon.propTypes = {
  children: PropTypes.node,
};

InputGroup.Addon.displayName = "InputGroup.Addon";

export default InputGroup;
