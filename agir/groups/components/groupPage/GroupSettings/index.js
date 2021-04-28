import PropTypes from "prop-types";
import React, { useMemo } from "react";

import { getMenuRoute, getRoutes } from "./routes.config";

import ObjectManagement from "@agir/front/genericComponents/ObjectManagement";

export const GroupSettings = (props) => {
  const { group, basePath } = props;

  const routes = useMemo(() => getRoutes(basePath), [basePath]);
  const menuRoute = useMemo(() => getMenuRoute(basePath), [basePath]);

  if (!group || !group.isManager) {
    return null;
  }

  return (
    <ObjectManagement
      title={group?.name}
      object={group}
      group={group}
      groupPk={group?.id}
      basePath={basePath}
      routes={routes}
      menuRoute={menuRoute}
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
