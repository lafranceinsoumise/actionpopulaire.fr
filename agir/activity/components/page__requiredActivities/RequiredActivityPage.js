import { Helmet } from "react-helmet";
import React from "react";

import NotificationSettings from "@agir/activity/common/notificationSettings/NotificationSettings";
import RequiredActivityList from "./RequiredActivityList";

const ActivityPage = (props) => (
  <>
    <Helmet>
      <title>Actualités - Action populaire</title>
    </Helmet>
    <RequiredActivityList {...props} />
    <NotificationSettings />
  </>
);

export default ActivityPage;
