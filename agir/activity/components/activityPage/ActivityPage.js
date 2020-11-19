import React from "react";

import Layout, { LayoutTitle } from "@agir/front/dashboardComponents/Layout";
import ActivityList from "@agir/activity/activityPage/ActivityList";

import styled from "styled-components";
import style from "@agir/front/genericComponents/_variables.scss";

const Page = styled.article`
  margin: 0;

  @media (max-width: ${style.collapse}px) {
    margin: 25px 0;
  }
`;

const ActivityPage = (props) => (
  <Layout active="activity">
    <Page>
      <LayoutTitle>Notifications</LayoutTitle>
      <ActivityList {...props} />
    </Page>
  </Layout>
);

export default ActivityPage;
