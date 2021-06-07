import { Helmet } from "react-helmet";
import React from "react";

import NotificationSettings from "@agir/activity/NotificationSettings/NotificationSettings";
import ActivityList from "./ActivityList";

const ActivityPage = (props) => (
  <>
    <Helmet>
      <title>Actualités - Action populaire</title>
    </Helmet>
    <ActivityList {...props} />
    <NotificationSettings />
  </>
);

export default ActivityPage;
