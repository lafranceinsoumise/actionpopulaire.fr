import PropTypes from "prop-types";
import React from "react";
import { Link as RouterLink } from "react-router-dom";

import { useSelector } from "@agir/front/globalContext/GlobalContext";
import { getRoutes } from "@agir/front/globalContext/reducers";
import { getRouteByPathname } from "@agir/front/app/routes.config";

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
  component: PropTypes.elementType,
};

const RouteLink = (props) => {
  const { route, ...rest } = props;
  const routes = useSelector(getRoutes);

  const { url, isExternal = false } = React.useMemo(
    () => ({
      url: routes[route],
      isExternal: !getRouteByPathname(routes[route]),
    }),
    [routes, route]
  );

  return isExternal ? (
    <ExternalLink {...rest} href={url} />
  ) : (
    <RouterLink {...rest} to={url} />
  );
};
RouteLink.propTypes = {
  route: PropTypes.string.isRequired,
};

const Link = (props) => {
  const { route, href, to } = props;
  if (route) {
    return <RouteLink {...props} />;
  }
  if (href) {
    return <ExternalLink {...props} />;
  }
  if (to) {
    return <RouterLink to={to} {...props} />;
  }

  return null;
};
Link.propTypes = {
  route: PropTypes.string,
  href: PropTypes.string,
  to: PropTypes.oneOfType([PropTypes.string, PropTypes.func, PropTypes.object]),
};
export default Link;
