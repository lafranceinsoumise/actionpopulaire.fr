import React, { useEffect, useMemo } from "react";
import { useTransition, animated } from "@react-spring/web";
import styled from "styled-components";
import useSWR from "swr";

import style from "@agir/front/genericComponents/_variables.scss";

import { useSelector } from "@agir/front/globalContext/GlobalContext";
import { getRoutes } from "@agir/front/globalContext/reducers";
import { getUnread } from "@agir/activity/common/helpers";
import { setAllActivitiesAsRead } from "@agir/activity/common/api";

import {
  LayoutSubtitle,
  LayoutTitle,
} from "@agir/front/dashboardComponents/Layout";
import { PageFadeIn } from "@agir/front/genericComponents/PageFadeIn";
import Skeleton from "@agir/front/genericComponents/Skeleton";

import NotificationSettingLink from "@agir/activity/NotificationSettings/NotificationSettingLink";

import ActivityCard from "./ActivityCard";
import EmptyActivityList from "./EmptyActivityList";

export const StyledList = styled.ul``;
const Page = styled.article`
  @media (max-width: ${style.collapse}px) {
    padding-bottom: 48px;
  }

  ${StyledList} {
    list-style: none;
    max-width: 711px;
    margin: 0;
    width: 100%;
    padding: 1.5rem 0;

    @media (max-width: ${style.collapse}px) {
      padding: 0 0 0.5rem;
      margin: 0 auto;
      max-width: 100%;
    }

    li {
      margin: 0;
      margin-bottom: 16px;
    }
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

  const transitions = useTransition(activities, {
    keys: ({ id }) => id,
    initial: { transform: "translate3d(0,0,0)" },
    enter: { opacity: 1, marginBottom: 16, maxHeight: "1000px" },
    leave: { opacity: 0, marginBottom: 0, maxHeight: "0px" },
  });

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
          Notifications
          <NotificationSettingLink root="activite" />
        </LayoutTitle>
        <LayoutSubtitle>
          L'actualité de vos groupes et de votre engagement
        </LayoutSubtitle>
        {Array.isArray(activities) && (
          <div>
            {activities.length > 0 ? (
              <StyledList type="activities">
                {transitions((style, activity) => (
                  <animated.li style={style}>
                    <ActivityCard routes={routes} {...activity} />
                  </animated.li>
                ))}
              </StyledList>
            ) : (
              <EmptyActivityList />
            )}
          </div>
        )}
      </PageFadeIn>
    </Page>
  );
};
export default ActivityList;
