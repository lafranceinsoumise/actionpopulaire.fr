import React from "react";

import NotificationSettings from "@agir/notifications/NotificationSettings/NotificationSettings";
import ActivityList from "./ActivityList";

const ActivityPage = (props) => (
  <>
    <ActivityList {...props} />
    <NotificationSettings />
  </>
);

export default ActivityPage;
