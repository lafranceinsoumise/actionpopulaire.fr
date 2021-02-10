import PropTypes from "prop-types";
import React from "react";

import GroupEventList from "@agir/groups/groupPage/GroupEventList";
import {
  MemberEmptyEvents,
  ManagerEmptyEvents,
} from "@agir/groups/groupPage/EmptyContent";

const AgendaRoute = ({
  group,
  allEvents,
  upcomingEvents,
  pastEvents,
  loadMorePastEvents,
  isLoadingPastEvents,
  hasTabs,
}) => (
  <>
    {Array.isArray(upcomingEvents) && upcomingEvents.length > 0 ? (
      <GroupEventList title="Événements à venir" events={upcomingEvents} />
    ) : null}
    {Array.isArray(pastEvents) && pastEvents.length > 0 ? (
      <GroupEventList
        title="Événements passés"
        events={pastEvents}
        loadMore={loadMorePastEvents}
        isLoading={isLoadingPastEvents}
      />
    ) : null}
    {allEvents.length === 0 && hasTabs && group.isManager ? (
      <ManagerEmptyEvents />
    ) : null}
    {allEvents.length === 0 && hasTabs && !group.isManager && group.isMember ? (
      <MemberEmptyEvents />
    ) : null}
  </>
);
AgendaRoute.propTypes = {
  group: PropTypes.object,
  allEvents: PropTypes.arrayOf(PropTypes.object),
  upcomingEvents: PropTypes.arrayOf(PropTypes.object),
  pastEvents: PropTypes.arrayOf(PropTypes.object),
  isLoadingPastEvents: PropTypes.bool,
  loadMorePastEvents: PropTypes.func,
  hasTabs: PropTypes.bool,
};

export default AgendaRoute;
