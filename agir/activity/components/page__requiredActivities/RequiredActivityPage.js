import React from "react";

import Layout, { LayoutTitle } from "@agir/front/dashboardComponents/Layout";
import RequiredActivityList from "./RequiredActivityList";

import styled from "styled-components";
import style from "@agir/front/genericComponents/_variables.scss";

const Page = styled.article`
  margin: 0;

  @media (max-width: ${style.collapse}px) {
    margin: 25px 0;
  }
`;

const RequiredActivityPage = (props) => (
  <Layout active="required-activity">
    <Page>
      <LayoutTitle>À traiter</LayoutTitle>
      <RequiredActivityList {...props} />
    </Page>
  </Layout>
);

export default RequiredActivityPage;
