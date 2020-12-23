import PropTypes from "prop-types";
import React from "react";
import { Link as RouterLink } from "react-router-dom";

const ExternalLink = (props) => {
  const { href, component, ...rest } = props;

  if (component) {
    const Component = component;
    return <Component href={href} {...rest} />;
  }

  return <a href={href} {...rest} />;
};
ExternalLink.propTypes = {
  href: PropTypes.string.isRequired,
  component: PropTypes.oneOfType([PropTypes.element, PropTypes.func]),
};

const Link = (props) => {
  const { href, to, component, ...rest } = props;

  if (href) {
    return <ExternalLink {...props} />;
  }

  if (to) {
    return <RouterLink to={to} component={component} {...rest} />;
  }

  return null;
};
Link.propTypes = {
  href: PropTypes.string,
  to: PropTypes.oneOfType([PropTypes.string, PropTypes.func, PropTypes.object]),
  component: PropTypes.oneOfType([PropTypes.element, PropTypes.func]),
};
export default Link;
