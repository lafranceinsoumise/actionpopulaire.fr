import { Helmet } from "react-helmet";
import React from "react";

import ActivityList from "./ActivityList";

const ActivityPage = (props) => (
  <>
    <Helmet>
      <title>Actualités - Action populaire</title>
    </Helmet>
    <ActivityList {...props} />
  </>
);

export default ActivityPage;
