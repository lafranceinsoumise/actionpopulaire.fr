import React, { useEffect, useMemo } from "react";

import {
  useDispatch,
  useSelector,
} from "@agir/front/globalContext/GlobalContext";
import { setAllActivitiesAsRead } from "@agir/front/globalContext/actions";
import { getActivities, getRoutes } from "@agir/front/globalContext/reducers";

import { getUnread } from "@agir/activity/common/helpers";

import Activities from "@agir/activity/common/Activities";
import ActivityCard from "./ActivityCard";

const ActivityList = () => {
  const dispatch = useDispatch();
  const activities = useSelector(getActivities);
  const routes = useSelector(getRoutes);
  const unreadActivities = useMemo(() => getUnread(activities), [activities]);

  useEffect(() => {
    if (unreadActivities.length > 0) {
      dispatch(setAllActivitiesAsRead(unreadActivities.map(({ id }) => id)));
    }
  }, [dispatch, unreadActivities]);

  return (
    <Activities
      CardComponent={ActivityCard}
      activities={activities}
      routes={routes}
    />
  );
};
export default ActivityList;
