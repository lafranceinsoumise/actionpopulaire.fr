import React, { useState, useMemo, useEffect, useCallback } from "react";

import { parseActivities } from "@agir/activity/common/helpers";
import { useGlobalContext } from "@agir/front/genericComponents/GlobalContext";
import Activities from "@agir/activity/common/Activities";

import RequiredActionCard from "./RequiredActionCard";

const RequiredActivityList = () => {
  const { activities, dispatch } = useGlobalContext();

  const [dismissed, setDismissed] = useState([]);
  const handleDismiss = useCallback((id) => {
    // TODO: Actually update the activity status
    setDismissed((state) => [...state, id]);
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
