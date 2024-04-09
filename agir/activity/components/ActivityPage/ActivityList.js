import React, { useCallback, useEffect, useMemo } from "react";
import styled from "styled-components";
import useSWR from "swr";

import * as style from "@agir/front/genericComponents/_variables.scss";

import { useIsOffline } from "@agir/front/offline/hooks";
import { useSelector } from "@agir/front/globalContext/GlobalContext";
import { getRoutes } from "@agir/front/globalContext/reducers";
import { getUnread } from "@agir/activity/common/helpers";
import { useActivities } from "@agir/activity/common/hooks";
import {
  setAllActivitiesAsRead,
  setActivityAsInteracted,
} from "@agir/activity/common/api";
import { useInfiniteScroll } from "@agir/lib/utils/hooks";

import {
  LayoutSubtitle,
  LayoutTitle,
} from "@agir/front/app/Layout/StyledComponents";
import { PageFadeIn } from "@agir/front/genericComponents/PageFadeIn";
import Skeleton from "@agir/front/genericComponents/Skeleton";

import NotificationSettingLink from "@agir/notifications/NotificationSettings/NotificationSettingLink";
import NotFoundPage from "@agir/front/notFoundPage/NotFoundPage";

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
    }
  }
`;

const ActivityList = () => {
  const isOffline = useIsOffline();
  const routes = useSelector(getRoutes);

  const { data: session } = useSWR("/api/session/");
  const { activities, isLoadingInitialData, isLoadingMore, loadMore } =
    useActivities();
  const unreadActivities = useMemo(() => getUnread(activities), [activities]);

  useEffect(() => {
    if (unreadActivities.length > 0) {
      setAllActivitiesAsRead();
    }
  }, [unreadActivities]);

  const onClickActivity = useCallback(setActivityAsInteracted, []);

  const lastItemRef = useInfiniteScroll(loadMore, isLoadingMore);

  return (
    <Page>
      <PageFadeIn
        ready={session && !isLoadingInitialData}
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
          L'actualité de vos groupes et de votre engagement. Cliquez sur une
          notification pour la marquer comme “acquittée”.
        </LayoutSubtitle>
        {Array.isArray(activities) && (
          <div>
            {activities.length > 0 ? (
              <StyledList type="activities">
                {activities.map((activity, i) => (
                  <li
                    key={activity.id}
                    ref={i + 1 === activities.length ? lastItemRef : null}
                  >
                    <ActivityCard
                      routes={routes}
                      {...activity}
                      onClick={onClickActivity}
                    />
                  </li>
                ))}
                {isLoadingMore && <Skeleton />}
              </StyledList>
            ) : isOffline ? (
              <NotFoundPage hasTopBar={false} reloadOnReconnection={false} />
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
