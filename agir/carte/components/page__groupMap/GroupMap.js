import React from "react";

import { useGlobalContext } from "@agir/front/genericComponents/GlobalContext";
import MapPage from "@agir/carte/common/MapPage";

const GroupMap = () => {
  const { user, routes } = useGlobalContext();

  if (!routes || !routes.groupsMap) {
    return null;
  }

  return (
    <MapPage
      type="groups"
      back={routes.groups}
      create={routes.createGroup}
      map={routes.groupsMap}
      user={user}
    />
  );
};

export default GroupMap;
