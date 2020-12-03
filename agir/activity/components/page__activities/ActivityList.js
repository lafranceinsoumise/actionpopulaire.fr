import React, { useMemo } from "react";

import { parseActivities } from "@agir/activity/common/helpers";
import { useGlobalContext } from "@agir/front/genericComponents/GlobalContext";
import Activities from "@agir/activity/common/Activities";
import ActivityCard from "./ActivityCard";

const ActivityList = () => {
  const { activities } = useGlobalContext();
  const { unrequired } = useMemo(() => parseActivities(activities), [
    activities,
  ]);

  return <Activities CardComponent={ActivityCard} activities={unrequired} />;
};
export default ActivityList;
