import PropTypes from "prop-types";
import React, { useEffect, useMemo } from "react";
import { Redirect } from "react-router-dom";

import { routeConfig } from "@agir/front/app/routes.config";
import { useGroupMessage } from "@agir/groups/groupPage/hooks";

import {
  useDispatch,
  useSelector,
} from "@agir/front/globalContext/GlobalContext";
import {
  setBackLink,
  setTopBarRightLink,
} from "@agir/front/globalContext/actions";
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

const PageSkeleton = <Skeleton />;

const Page = ({ groupPk, messagePk }) => {
  const isSessionLoaded = useSelector(getIsSessionLoaded);
  const backLink = useSelector(getBackLink);
  const user = useSelector(getUser);
  const dispatch = useDispatch();

  const { group, message, events, loadMoreEvents, isLoading } = useGroupMessage(
    groupPk,
    messagePk
  );

  const messageURL = useMemo(
    () =>
      routeConfig.groupMessage &&
      routeConfig.groupMessage.getLink({
        groupPk,
        messagePk,
      }),
    [groupPk, messagePk]
  );

  const groupURL = useMemo(
    () =>
      routeConfig.groupDetails &&
      routeConfig.groupDetails.getLink({
        groupPk,
        activeTab: "discussion",
      }),
    [groupPk]
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
                to: routeConfig.groups.getLink(),
                label: "Retour à l'accueil",
              }
        )
      );
  }, [backLink, group, groupURL, dispatch]);

  useEffect(() => {
    if (group && group.isManager && group.routes && group.routes.settings) {
      dispatch(
        setTopBarRightLink({
          href: group.routes.settings,
          label: "Gestion du groupe",
        })
      );
    } else {
      dispatch(setTopBarRightLink(null));
    }
  }, [group, dispatch]);

  if (isSessionLoaded && group && group.isMember && message === null) {
    const redirectTo =
      group.id && routeConfig.groupDetails
        ? routeConfig.groupDetails.getLink({ groupPk: group.id })
        : routeConfig.groups.getLink();

    return <Redirect to={redirectTo} />;
  }

  return (
    <CenteredLayout
      backLink={isSessionLoaded && group ? backLink : undefined}
      $maxWidth="780px"
      title={
        group && !group.isMember
          ? "Cette discussion n'est pas disponible"
          : undefined
      }
      icon={group && !group.isMember ? "lock" : undefined}
    >
      <PageFadeIn wait={PageSkeleton} ready={isSessionLoaded && group}>
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
      </PageFadeIn>
    </CenteredLayout>
  );
};
Page.propTypes = {
  groupPk: PropTypes.string.isRequired,
  messagePk: PropTypes.string.isRequired,
};

export default Page;
