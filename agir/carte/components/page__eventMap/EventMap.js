import React from "react";

import { useGlobalContext } from "@agir/front/genericComponents/GlobalContext";
import MapPage from "@agir/carte/common/MapPage";

const EventMap = () => {
  const { user, routes } = useGlobalContext();

  if (!routes || !routes.eventsMap) {
    return null;
  }

  return (
    <MapPage
      type="events"
      back={routes.events}
      create={routes.createEvent}
      map={routes.eventsMap}
      user={user}
    />
  );
};

export default EventMap;
