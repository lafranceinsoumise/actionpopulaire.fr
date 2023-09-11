import PropTypes from "prop-types";
import React, { useEffect, useMemo } from "react";
import { Redirect } from "react-router-dom";

import { getMessageSubject } from "@agir/msgs/common/utils";
import { routeConfig } from "@agir/front/app/routes.config";
import { useGroupMessage } from "@agir/groups/groupPage/hooks";
import { useIsOffline } from "@agir/front/offline/hooks";

import {
  useDispatch,
  useSelector,
} from "@agir/front/globalContext/GlobalContext";
import {
  setBackLink,
  setAdminLink,
  setPageTitle,
  setTopBarRightLink,
} from "@agir/front/globalContext/actions";
import {
  getIsSessionLoaded,
  getUser,
  getBackLink,
} from "@agir/front/globalContext/reducers";

import CenteredLayout from "@agir/front/app/Layout/CenteredLayout";
import NotFoundPage from "@agir/front/notFoundPage/NotFoundPage";
import OpenGraphTags from "@agir/front/app/OpenGraphTags";
import PageFadeIn from "@agir/front/genericComponents/PageFadeIn";
import Skeleton from "@agir/front/genericComponents/Skeleton";

import GroupMessagePage from "./GroupMessagePage";
import UnavailableMessagePage from "./UnavailableMessagePage";

const PageSkeleton = <Skeleton />;

const Page = ({ groupPk, messagePk }) => {
  const isOffline = useIsOffline();
  const isSessionLoaded = useSelector(getIsSessionLoaded);
  const backLink = useSelector(getBackLink);
  const user = useSelector(getUser);
  const dispatch = useDispatch();

  const { group, message, events, loadMoreEvents, isLoading } = useGroupMessage(
    groupPk,
    messagePk,
  );

  const messageURL = useMemo(
    () =>
      routeConfig.groupMessage &&
      routeConfig.groupMessage.getLink({
        groupPk,
        messagePk,
      }),
    [groupPk, messagePk],
  );

  const groupURL = useMemo(
    () =>
      routeConfig.groupDetails &&
      routeConfig.groupDetails.getLink({
        groupPk,
        activeTab: "messages",
      }),
    [groupPk],
  );

  useEffect(() => {
    !backLink &&
      dispatch(
        setBackLink(
          group && group.isMember
            ? {
                to: groupURL,
                label: "Voir le groupe",
              }
            : {
                route: "groups",
              },
        ),
      );
  }, [backLink, group, groupURL, dispatch]);

  useEffect(() => {
    if (group && group.routes && group.routes.admin) {
      dispatch(
        setAdminLink({
          href: group.routes.admin,
          label: "Administration",
        }),
      );
    }
  }, [group, dispatch]);

  useEffect(() => {
    const pageTitle = message
      ? getMessageSubject(message)
      : "Message du groupe";
    dispatch(setPageTitle(pageTitle));
    dispatch(setTopBarRightLink({ message: message }));
  }, [dispatch, message]);

  if (isOffline && (!group || !message)) {
    return <NotFoundPage reloadOnReconnection={false} hasTopBar={false} />;
  }

  if (
    !isLoading &&
    isSessionLoaded &&
    group &&
    group.isMember &&
    message === null
  ) {
    const redirectTo =
      group.id && routeConfig.groupDetails
        ? routeConfig.groupDetails.getLink({ groupPk: group.id })
        : routeConfig.groups.getLink();
    return <Redirect to={redirectTo} />;
  }

  return (
    <>
      <OpenGraphTags
        title={
          group && group.name && group.isMember
            ? `Message du groupe : ${group.name}`
            : "Message du groupe"
        }
      />
      <PageFadeIn wait={PageSkeleton} ready={isSessionLoaded && group}>
        {isSessionLoaded && group ? (
          <CenteredLayout
            $maxWidth="780px"
            title={
              group && !group.isMember
                ? "Ce message n'est pas disponible"
                : undefined
            }
            icon={group && !group.isMember ? "lock" : undefined}
          >
            {group && group.isMember ? (
              <PageFadeIn wait={PageSkeleton} ready={!isLoading}>
                <GroupMessagePage
                  group={group}
                  user={user}
                  events={events}
                  message={message}
                  messageURL={messageURL}
                  groupURL={groupURL}
                  loadMoreEvents={loadMoreEvents}
                  isLoading={isLoading}
                />
              </PageFadeIn>
            ) : (
              <UnavailableMessagePage groupURL={groupURL} />
            )}
          </CenteredLayout>
        ) : null}
      </PageFadeIn>
    </>
  );
};
Page.propTypes = {
  groupPk: PropTypes.string.isRequired,
  messagePk: PropTypes.string.isRequired,
};

export default Page;
