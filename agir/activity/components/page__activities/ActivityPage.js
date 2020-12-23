import { Helmet } from "react-helmet";
import React from "react";
import style from "@agir/front/genericComponents/_variables.scss";

import Layout from "@agir/front/dashboardComponents/Layout";
import ActivityList from "./ActivityList";

const ActivityPage = (props) => (
  <Layout
    active="activity"
    smallBackgroundColor={style.black25}
    title="Actualités"
    subtitle="L'actualité de vos groupes et de votre engagement"
  >
    <Helmet>
      <title>Actualités - Action populaire</title>
    </Helmet>
    <ActivityList {...props} />
  </Layout>
);

export default ActivityPage;
