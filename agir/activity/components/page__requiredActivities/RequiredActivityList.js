import React, { useCallback, useMemo, useState } from "react";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

import { useSelector } from "@agir/front/globalContext/GlobalContext";
import { getRoutes } from "@agir/front/globalContext/reducers";
import {
  activityStatus,
  getUninteracted,
  getUninteractedCount,
} from "@agir/activity/common/helpers";

import FilterTabs from "@agir/front/genericComponents/FilterTabs";
import Activities from "@agir/activity/common/Activities";
import NotificationSettingLink from "@agir/activity/common/notificationSettings/NotificationSettingLink";

import {
  LayoutSubtitle,
  LayoutTitle,
} from "@agir/front/dashboardComponents/Layout";
import RequiredActionCard from "./RequiredActionCard";
import { PageFadeIn } from "@agir/front/genericComponents/PageFadeIn";
import Skeleton from "@agir/front/genericComponents/Skeleton";
import useSWR from "swr";
import {
  dismissRequiredActionActivity,
  undoRequiredActionActivityDismissal,
} from "@agir/activity/common/actions";

const Page = styled.article`
  margin: 0;

  @media (max-width: ${style.collapse}px) {
    padding-bottom: 48px;
  }
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
`;

const RequiredActivityList = () => {
  const routes = useSelector(getRoutes);
  const session = useSWR("/api/session/");
  let { data: activities } = useSWR("/api/user/required-activities/");
  let uninteractedCount = getUninteractedCount(activities);

  const [displayAll, setDisplayAll] = useState(false);
  const toggleDisplayAll = useCallback((shouldDisplayAll) => {
    setDisplayAll(Boolean(shouldDisplayAll));
  }, []);

  const handleDismiss = async (id, status) => {
    if (status !== activityStatus.STATUS_INTERACTED) {
      await dismissRequiredActionActivity(id);
    } else {
      await undoRequiredActionActivityDismissal(id);
    }
  };

  const visibleActivities = useMemo(
    () => (displayAll ? activities : getUninteracted(activities)),
    [displayAll, activities]
  );

  const tabs = useMemo(() => ["non traité", "voir tout"], []);

  return (
    <Page>
      <LayoutTitle>
        {uninteractedCount ? <Counter>{uninteractedCount}</Counter> : null}À
        faire
        <NotificationSettingLink root="a-traiter" />
      </LayoutTitle>
      <LayoutSubtitle>
        Vos actions à traiter en priorité, pour ne rien oublier !
      </LayoutSubtitle>
      <PageFadeIn
        ready={session && activities}
        wait={
          <div style={{ marginTop: "32px" }}>
            <Skeleton />
          </div>
        }
      >
        <FilterTabs
          style={{ marginBottom: "1rem" }}
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
  );
};
export default RequiredActivityList;
