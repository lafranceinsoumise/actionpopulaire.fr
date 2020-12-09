import React from "react";

import { useSelector } from "@agir/front/globalContext/GlobalContext";
import { getActivities } from "@agir/front/globalContext/reducers";

import Activities from "@agir/activity/common/Activities";
import ActivityCard from "./ActivityCard";

const ActivityList = () => {
  const activities = useSelector(getActivities);

  return <Activities CardComponent={ActivityCard} activities={activities} />;
};
export default ActivityList;
