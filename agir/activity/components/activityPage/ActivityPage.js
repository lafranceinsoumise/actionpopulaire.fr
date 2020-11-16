import React from "react";

import Layout from "@agir/front/dashboardComponents/Layout";
import ActivityList from "@agir/activity/activityPage/ActivityList";

const ActivityPage = (props) => (
  <Layout active="activity" title="Notifications">
    <ActivityList {...props} />
  </Layout>
);

export default ActivityPage;
