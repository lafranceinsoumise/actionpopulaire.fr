import React, { useCallback, useMemo, useState } from "react";
import { Helmet } from "react-helmet";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

import {
  useDispatch,
  useSelector,
} from "@agir/front/globalContext/GlobalContext";
import {
  getIsSessionLoaded,
  getRequiredActionActivities,
  getRoutes,
} from "@agir/front/globalContext/reducers";
import { dismissRequiredActionActivity } from "@agir/front/globalContext/actions";
import { activityStatus } from "@agir/activity/common/helpers";

import FilterTabs from "@agir/front/genericComponents/FilterTabs";
import Activities from "@agir/activity/common/Activities";

import {
  LayoutTitle,
  LayoutSubtitle,
} from "@agir/front/dashboardComponents/Layout";
import RequiredActionCard from "./RequiredActionCard";
import { PageFadeIn } from "@agir/front/genericComponents/PageFadeIn";
import Skeleton from "@agir/front/genericComponents/Skeleton";

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
  const isSessionLoaded = useSelector(getIsSessionLoaded);
  const activities = useSelector(getRequiredActionActivities);
  const routes = useSelector(getRoutes);
  const dispatch = useDispatch();

  const [displayAll, setDisplayAll] = useState(false);
  const toggleDisplayAll = useCallback((shouldDisplayAll) => {
    setDisplayAll(Boolean(shouldDisplayAll));
  }, []);

  const handleDismiss = useCallback(
    async (id) => {
      dispatch(dismissRequiredActionActivity(id));
    },
    [dispatch]
  );

  const visibleActivities = useMemo(
    () =>
      activities.filter(
        ({ status }) =>
          displayAll || status !== activityStatus.STATUS_INTERACTED
      ),
    [displayAll, activities]
  );

  const tabs = useMemo(() => ["non traité", "voir tout"], []);

  return (
    <>
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
        <PageFadeIn
          ready={isSessionLoaded}
          wait={
            <div style={{ marginTop: "32px" }}>
              <Skeleton />
            </div>
          }
        >
          <FilterTabs
            style={{ marginTop: "2rem", marginBottom: "1rem" }}
            tabs={tabs}
            onTabChange={toggleDisplayAll}
          />
          <Activities
            CardComponent={RequiredActionCard}
            activities={visibleActivities}
            onDismiss={handleDismiss}
            routes={routes}
          />
        </PageFadeIn>
      </Page>
    </>
  );
};
export default RequiredActivityList;
