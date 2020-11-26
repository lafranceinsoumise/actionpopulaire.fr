import React from "react";
import style from "@agir/front/genericComponents/_variables.scss";

import Layout from "@agir/front/dashboardComponents/Layout";
import ActivityList from "./ActivityList";

const ActivityPage = (props) => (
  <Layout
    active="activity"
    smallBackgroundColor={style.black25}
    title="Notifications"
    subtitle="L'actualité de vos groupes et de la France Insoumise"
  >
    <ActivityList {...props} />
  </Layout>
);

export default ActivityPage;
