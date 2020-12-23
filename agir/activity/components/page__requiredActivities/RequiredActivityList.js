import { Helmet } from "react-helmet";
import React, { useCallback } from "react";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

import {
  useDispatch,
  useSelector,
} from "@agir/front/globalContext/GlobalContext";
import {
  getRequiredActionActivities,
  getRoutes,
} from "@agir/front/globalContext/reducers";
import { dismissRequiredActionActivity } from "@agir/front/globalContext/actions";

import Activities from "@agir/activity/common/Activities";

import Layout, {
  LayoutTitle,
  LayoutSubtitle,
} from "@agir/front/dashboardComponents/Layout";
import RequiredActionCard from "./RequiredActionCard";

const Page = styled.article`
  margin: 0;
`;

const Counter = styled.span`
  background-color: ${style.redNSP};
  color: ${style.white};
  font-size: 13px;
  height: 2em;
  width: 2em;
  border-radius: 100%;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-variant-numeric: tabular-nums;
  margin-right: 12px;

  @media (max-width: ${style.collapse}px) {
  }
`;

const RequiredActivityList = () => {
  const activities = useSelector(getRequiredActionActivities);
  const routes = useSelector(getRoutes);
  const dispatch = useDispatch();

  const handleDismiss = useCallback(
    async (id) => {
      dispatch(dismissRequiredActionActivity(id));
    },
    [dispatch]
  );

  return (
    <Layout active="required-activity">
      <Helmet>
        <title>À faire - Action populaire</title>
      </Helmet>
      <Page>
        <LayoutTitle>
          {activities.length ? <Counter>{activities.length}</Counter> : null}À
          faire
        </LayoutTitle>
        <LayoutSubtitle>
          Vos actions à traiter en priorité, pour ne rien oublier !
        </LayoutSubtitle>
        <Activities
          CardComponent={RequiredActionCard}
          activities={activities}
          onDismiss={handleDismiss}
          routes={routes}
        />
      </Page>
    </Layout>
  );
};
export default RequiredActivityList;
