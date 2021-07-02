import PropTypes from "prop-types";
import React from "react";

import GroupPageComponent from "./GroupPage";
import NewGroupPageModal from "@agir/groups/groupPage/NewGroupPageModal";

import { useSelector } from "@agir/front/globalContext/GlobalContext";

import {
  getIsSessionLoaded,
  getIsConnected,
  getBackLink,
  getUser,
} from "@agir/front/globalContext/reducers";

import { useCustomAnnouncement } from "@agir/activity/common/hooks";

import { useGroupDetail } from "@agir/groups/groupPage/hooks";

const GroupPage = (props) => {
  const { groupPk } = props;
  const isSessionLoaded = useSelector(getIsSessionLoaded);
  const isConnected = useSelector(getIsConnected);
  const backLink = useSelector(getBackLink);
  const user = useSelector(getUser);

  const {
    group,
    groupSuggestions,
    allEvents,
    upcomingEvents,
    pastEvents,
    loadMorePastEvents,
    isLoadingPastEvents,
    pastEventReports,
    messages,
    loadMoreMessages,
    isLoadingMessages,
  } = useGroupDetail(groupPk);

  const [hasNewGroupPageModal, onCloseNewGroupPageModal] =
    useCustomAnnouncement("NewGroupPageModal");

  return (
    <>
      <NewGroupPageModal
        isActive={!!hasNewGroupPageModal}
        onClose={onCloseNewGroupPageModal}
      />
      <GroupPageComponent
        backLink={backLink}
        isConnected={isSessionLoaded && isConnected}
        isLoading={!isSessionLoaded || group === undefined}
        group={group}
        allEvents={allEvents}
        upcomingEvents={upcomingEvents}
        pastEvents={pastEvents}
        isLoadingPastEvents={isLoadingPastEvents}
        loadMorePastEvents={loadMorePastEvents}
        pastEventReports={pastEventReports}
        messages={messages}
        isLoadingMessages={isLoadingMessages}
        loadMoreMessages={loadMoreMessages}
        groupSuggestions={
          Array.isArray(groupSuggestions) ? groupSuggestions : []
        }
        user={user}
      />
    </>
  );
};
GroupPage.propTypes = {
  groupPk: PropTypes.string,
  messagePk: PropTypes.string,
};
export default GroupPage;
