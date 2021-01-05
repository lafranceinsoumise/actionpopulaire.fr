import React from "react";

import { useSelector } from "@agir/front/globalContext/GlobalContext";
import { getRoutes, getUser } from "@agir/front/globalContext/reducers";
import MapPage from "@agir/carte/common/MapPage";

const GroupMap = () => {
  const routes = useSelector(getRoutes);
  const user = useSelector(getUser);

  if (!routes || !routes.groupsMap) {
    return null;
  }

  return (
    <MapPage
      type="groups"
      backRoute="groups"
      createRoute="createGroup"
      mapURL={routes.groupsMap}
      user={user}
    />
  );
};

export default GroupMap;
