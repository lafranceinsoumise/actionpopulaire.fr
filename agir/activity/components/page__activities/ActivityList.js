import React, { useEffect, useMemo } from "react";

import {
  useDispatch,
  useSelector,
} from "@agir/front/globalContext/GlobalContext";
import { setAllActivitiesAsRead } from "@agir/front/globalContext/actions";
import {
  getActivities,
  getIsSessionLoaded,
  getRoutes,
} from "@agir/front/globalContext/reducers";

import { getUnread } from "@agir/activity/common/helpers";

import Activities from "@agir/activity/common/Activities";
import ActivityCard from "./ActivityCard";
import { PageFadeIn } from "@agir/front/genericComponents/PageFadeIn";
import Skeleton from "@agir/front/genericComponents/Skeleton";

const ActivityList = () => {
  const dispatch = useDispatch();
  const activities = useSelector(getActivities);
  const isSessionLoaded = useSelector(getIsSessionLoaded);
  const routes = useSelector(getRoutes);
  const unreadActivities = useMemo(() => getUnread(activities), [activities]);

  useEffect(() => {
    if (unreadActivities.length > 0) {
      dispatch(
        setAllActivitiesAsRead(
          unreadActivities.map(({ id }) => id),
          true
        )
      );
    }
  }, [dispatch, unreadActivities]);

  return (
    <PageFadeIn
      ready={isSessionLoaded}
      wait={
        <div style={{ marginTop: "32px" }}>
          <Skeleton />
        </div>
      }
    >
      <Activities
        CardComponent={ActivityCard}
        activities={activities}
        routes={routes}
      />
    </PageFadeIn>
  );
};
export default ActivityList;
