import PropTypes from "prop-types";
import React, { useEffect, useMemo } from "react";
import { Redirect } from "react-router-dom";

import { routeConfig } from "@agir/front/app/routes.config";
import { useGroupMessage } from "@agir/groups/groupPage/hooks";

import {
  useDispatch,
  useSelector,
} from "@agir/front/globalContext/GlobalContext";
import { setBackLink } from "@agir/front/globalContext/actions";
import {
  getIsSessionLoaded,
  getUser,
  getBackLink,
} from "@agir/front/globalContext/reducers";

import CenteredLayout from "@agir/front/dashboardComponents/CenteredLayout";
import PageFadeIn from "@agir/front/genericComponents/PageFadeIn";
import Skeleton from "@agir/front/genericComponents/Skeleton";

import GroupMessagePage from "./GroupMessagePage";
import UnavailableMessagePage from "./UnavailableMessagePage";

const PageSkeleton = (
  <CenteredLayout>
    <Skeleton />
  </CenteredLayout>
);

const Page = ({ groupPk, messagePk }) => {
  const isSessionLoaded = useSelector(getIsSessionLoaded);
  const backLink = useSelector(getBackLink);
  const user = useSelector(getUser);
  const dispatch = useDispatch();

  const {
    group,
    message,
    events,
    loadMoreEvents,
    updateMessage,
    createComment,
    reportMessage,
    deleteMessage,
    isLoading,
  } = useGroupMessage(groupPk, messagePk);

  const messageURL = useMemo(
    () =>
      routeConfig.groupMessage &&
      routeConfig.groupMessage.getLink({
        groupPk,
        messagePk,
      }),
    [groupPk, messagePk]
  );

  useEffect(() => {
    !backLink &&
      dispatch(
        setBackLink(
          group && group.isMember
            ? {
                to: routeConfig.groupDetails.getLink({
                  groupPk: group.id,
                  activeTab: "discussion",
                }),
                label: "Voir le groupe",
              }
            : {
                to: routeConfig.groups.getLink(),
                label: "Retour à l'accueil",
              }
        )
      );
  }, [backLink, group, dispatch]);

  if (isSessionLoaded && group && group.isMember && message === null) {
    const redirectTo =
      group.id && routeConfig.groupDetails
        ? routeConfig.groupDetails.getLink({ groupPk: group.id })
        : routeConfig.groups.getLink();

    return <Redirect to={redirectTo} />;
  }

  return (
    <PageFadeIn wait={PageSkeleton} ready={isSessionLoaded && group}>
      {group && group.isMember ? (
        <PageFadeIn wait={PageSkeleton} ready={!!message}>
          <GroupMessagePage
            group={group}
            user={user}
            events={events}
            message={message}
            messageURL={messageURL}
            loadMoreEvents={loadMoreEvents}
            updateMessage={updateMessage}
            createComment={createComment}
            reportMessage={reportMessage}
            deleteMessage={deleteMessage}
            isLoading={isLoading}
          />
        </PageFadeIn>
      ) : (
        <UnavailableMessagePage groupPk={groupPk} />
      )}
    </PageFadeIn>
  );
};
Page.propTypes = {
  groupPk: PropTypes.string.isRequired,
  messagePk: PropTypes.string.isRequired,
};

export default Page;
