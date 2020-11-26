import React, { useState, useMemo, useEffect, useCallback } from "react";

import { parseActivities } from "@agir/activity/common/helpers";
import { useGlobalContext } from "@agir/front/genericComponents/GlobalContext";
import { dismissActivity } from "@agir/activity/common/helpers";
import Activities from "@agir/activity/common/Activities";

import RequiredActionCard from "./RequiredActionCard";

const RequiredActivityList = () => {
  const { activities, dispatch } = useGlobalContext();

  const [dismissed, setDismissed] = useState([]);
  const handleDismiss = useCallback(async (id) => {
    const success = await dismissActivity(id);
    success && setDismissed((state) => [...state, id]);
  }, []);

  const { required } = useMemo(() => parseActivities(activities, dismissed), [
    activities,
    dismissed,
  ]);

  useEffect(() => {
    dispatch({
      type: "update-required-action-activities",
      requiredActionActivities: required,
    });
  }, [dispatch, required]);

  return (
    <Activities
      CardComponent={RequiredActionCard}
      activities={required}
      onDismiss={handleDismiss}
    />
  );
};
export default RequiredActivityList;
