import React from "react";

import { useLocation } from "react-router-dom";

import { useSelector } from "@agir/front/globalContext/GlobalContext";
import { getRoutes, getUser } from "@agir/front/globalContext/reducers";
import MapPage from "@agir/carte/common/MapPage";
import { routeConfig } from "@agir/front/app/routes.config";

const transmittedArgs = [
  "subtype",
  "include_past",
  "include_hidden",
  "bounds",
  "no_control",
];

const EventMap = () => {
  const routes = useSelector(getRoutes);
  const user = useSelector(getUser);
  const { search } = useLocation();

  const currentParams = new URLSearchParams(search);
  const newParams = new URLSearchParams();

  for (let [key, value] of currentParams.entries()) {
    if (transmittedArgs.includes(key)) {
      newParams.append(key, value);
    }
  }

  if (!routes || !routes.groupsMap) {
    return null;
  }

  return (
    <MapPage
      type="events"
      createLinkProps={{
        as: "Link",
        route: "createEvent",
        children: "Créer un événement dans mon quartier",
      }}
      searchUrl={routeConfig.searchEvent.path}
      mapURL={routes.eventsMap}
      mapParams={newParams.toString()}
      user={user}
    />
  );
};

export default EventMap;
