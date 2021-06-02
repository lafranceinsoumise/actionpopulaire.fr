import React, { useEffect, useMemo } from "react";
import styled from "styled-components";
import useSWR from "swr";

import style from "@agir/front/genericComponents/_variables.scss";

import { useSelector } from "@agir/front/globalContext/GlobalContext";
import { getRoutes } from "@agir/front/globalContext/reducers";

import { getUnread } from "@agir/activity/common/helpers";
import { setAllActivitiesAsRead } from "../common/actions";

import Activities from "@agir/activity/common/Activities";
import ActivityCard from "./ActivityCard";
import { PageFadeIn } from "@agir/front/genericComponents/PageFadeIn";
import Skeleton from "@agir/front/genericComponents/Skeleton";

import NotificationSettingLink from "@agir/activity/common/notificationSettings/NotificationSettingLink";

import {
  LayoutSubtitle,
  LayoutTitle,
} from "@agir/front/dashboardComponents/Layout";

const Page = styled.article`
  @media (max-width: ${style.collapse}px) {
    padding-bottom: 48px;
  }
`;

const ActivityList = () => {
  const routes = useSelector(getRoutes);

  const { data: session } = useSWR("/api/session/");
  const { data: activities } = useSWR("/api/user/activities/");
  const unreadActivities = useMemo(() => getUnread(activities), [activities]);

  useEffect(() => {
    if (unreadActivities.length > 0) {
      setAllActivitiesAsRead(unreadActivities.map(({ id }) => id));
    }
  }, [unreadActivities]);

  return (
    <Page>
      <PageFadeIn
        ready={session && activities}
        wait={
          <div style={{ marginTop: "32px" }}>
            <Skeleton />
          </div>
        }
      >
        <LayoutTitle>
          Actualités
          <NotificationSettingLink root="activite" />
        </LayoutTitle>
        <LayoutSubtitle>
          L'actualité de vos groupes et de votre engagement
        </LayoutSubtitle>
        <Activities
          CardComponent={ActivityCard}
          activities={activities}
          routes={routes}
        />
      </PageFadeIn>
    </Page>
  );
};
export default ActivityList;
