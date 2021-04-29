import PropTypes from "prop-types";
import React, { useMemo } from "react";
import { Redirect } from "react-router-dom";

import { getMenuRoute, getRoutes } from "./routes.config";

import ObjectManagement from "@agir/front/genericComponents/ObjectManagement";

export const GroupSettings = (props) => {
  const { group, basePath } = props;

  const routes = useMemo(() => getRoutes(basePath, group), [basePath, group]);
  const menuRoute = useMemo(() => getMenuRoute(basePath), [basePath]);

  if (!group) {
    return null;
  }

  if (!group.isManager) {
    return <Redirect to={basePath} />;
  }

  return (
    <ObjectManagement
      title={group?.name}
      groupPk={group?.id}
      basePath={basePath}
      routes={routes}
      menuLink={menuRoute.getLink()}
    />
  );
};
GroupSettings.propTypes = {
  group: PropTypes.shape({
    id: PropTypes.string,
    name: PropTypes.string,
    isManager: PropTypes.bool,
  }).isRequired,
  basePath: PropTypes.string.isRequired,
};

export default GroupSettings;
