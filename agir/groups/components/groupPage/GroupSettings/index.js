import PropTypes from "prop-types";
import React, { useMemo } from "react";

import { routeConfig as globalRouteConfig } from "@agir/front/app/routes.config";
import { getMenuRoute, getRoutes } from "./routes.config";
import { useAuthentication } from "@agir/front/authentication/hooks";
import { getGroupTypeWithLocation } from "@agir/groups/groupPage/utils";
import { useGroupWord } from "@agir/groups/utils/group";

import ObjectManagement from "@agir/front/genericComponents/ObjectManagement";

export const GroupSettings = (props) => {
  const { group, basePath } = props;
  const withGroupWord = useGroupWord(group);
  const routes = useMemo(() => getRoutes(basePath, group), [basePath, group]);
  const menuRoute = useMemo(() => getMenuRoute(basePath), [basePath]);
  const isAuthorized = useAuthentication(globalRouteConfig.groupSettings);
  const redirectTo = useMemo(() => {
    if (!group?.isManager) {
      return basePath;
    }
    if (isAuthorized === false) {
      return {
        pathname: globalRouteConfig.login.getLink(),
        state: { from: { pathname: menuRoute.getLink() } },
      };
    }
    return null;
  }, [group, isAuthorized, basePath, menuRoute]);

  const subtitle = useMemo(
    () =>
      group
        ? group?.type && !group?.is2022
          ? `Gestion de votre ${getGroupTypeWithLocation(
              group.type
            ).toLowerCase()}`
          : withGroupWord`Gestion de votre groupe d'actions`
        : "",
    [group, withGroupWord]
  );

  if (!group) {
    return null;
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
    is2022: PropTypes.bool,
    name: PropTypes.string,
    type: PropTypes.string,
    isManager: PropTypes.bool,
  }).isRequired,
  basePath: PropTypes.string.isRequired,
};

export default GroupSettings;
