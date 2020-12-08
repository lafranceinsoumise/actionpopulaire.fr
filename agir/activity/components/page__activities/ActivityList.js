import React, { useCallback } from "react";

import { dismissActivity } from "@agir/activity/common/helpers";
import { useGlobalContext } from "@agir/front/genericComponents/GlobalContext";

import Activities from "@agir/activity/common/Activities";
import ActivityCard from "./ActivityCard";

const ActivityList = () => {
  const { unrequiredActivities, dispatch } = useGlobalContext();

  const handleVisible = useCallback(
    async (id, status) => {
      const success = await dismissActivity(id, status);
      success &&
        dispatch({
          type: "mark-activity-as-read",
          id,
          status,
        });
    },
    [dispatch]
  );

  return (
    <Activities
      CardComponent={ActivityCard}
      activities={unrequiredActivities}
      onVisible={handleVisible}
    />
  );
};
export default ActivityList;
