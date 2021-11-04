import PropTypes from "prop-types";
import React, { useMemo } from "react";
import { useLocation, Navigate, useMatch } from "react-router-dom";
import { useIsDesktop } from "@agir/front/genericComponents/grid";

import { routeConfig as globalRouteConfig } from "@agir/front/app/routes.config";
import { getMenuRoute, getRoutes } from "./routes.config";
import { useAuthentication } from "@agir/front/authentication/hooks";
import { getGroupTypeWithLocation } from "@agir/groups/groupPage/utils";

import ObjectManagement from "@agir/front/genericComponents/ObjectManagement/ObjectManagement";

export const GroupSettings = (props) => {
  const { group, basePath } = props;
  const routes = useMemo(() => getRoutes(basePath, group), [basePath, group]);
  const menuRoute = useMemo(() => getMenuRoute(basePath), [basePath]);
  const isAuthorized = useAuthentication(globalRouteConfig.groupSettings);
  const { pathname } = useLocation();
  const isDesktop = useIsDesktop();

  const redirectTo = useMemo(() => {
    if (!group?.isManager) {
      return basePath;
    }
    if (isAuthorized === false) {
      return {
        pathname: globalRouteConfig.login.getLink(),
        state: { next: pathname },
      };
    }
    return null;
  }, [group, isAuthorized, basePath, pathname]);

  const subtitle = useMemo(
    () =>
      group?.type
        ? `Gestion de votre ${getGroupTypeWithLocation(
            group.type
          ).toLowerCase()}`
        : "",
    [group]
  );

  if (!group) {
    return null;
  }

  const routeMenuMatch = useMatch(menuRoute.path);

  // Open first panel on Desktop
  if (isDesktop && routeMenuMatch?.isExact) {
    return <Navigate to="membres/" />;
  }

  return (
    <ObjectManagement
      title={group?.name}
      subtitle={subtitle}
      groupPk={group?.id}
      basePath={basePath}
      routes={routes}
      menuLink={menuRoute.getLink()}
      redirectTo={redirectTo}
    />
  );
};
GroupSettings.propTypes = {
  group: PropTypes.shape({
    id: PropTypes.string,
    name: PropTypes.string,
    type: PropTypes.string,
    isManager: PropTypes.bool,
  }).isRequired,
  basePath: PropTypes.string.isRequired,
};

export default GroupSettings;
