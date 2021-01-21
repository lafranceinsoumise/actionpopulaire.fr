import PropTypes from "prop-types";
import React from "react";

import { ResponsiveLayout } from "@agir/front/genericComponents/grid";
import ShareCard from "@agir/front/genericComponents/ShareCard";

import GroupEventList from "@agir/groups/groupPage/GroupEventList";
import GroupLocation from "@agir/groups/groupPage/GroupLocation";
import GroupDescription from "@agir/groups/groupPage/GroupDescription";
import {
  MemberEmptyEvents,
  ManagerEmptyEvents,
} from "@agir/groups/groupPage/EmptyContent";

const MobileAgendaRoute = ({
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
MobileAgendaRoute.propTypes = {
  group: PropTypes.object,
  allEvents: PropTypes.arrayOf(PropTypes.object),
  upcomingEvents: PropTypes.arrayOf(PropTypes.object),
  pastEvents: PropTypes.arrayOf(PropTypes.object),
  isLoadingPastEvents: PropTypes.bool,
  loadMorePastEvents: PropTypes.func,
  hasTabs: PropTypes.bool,
};

const DesktopAgendaRoute = ({
  group,
  allEvents,
  upcomingEvents,
  pastEvents,
  loadMorePastEvents,
  isLoadingPastEvents,
  hasTabs,
}) =>
  Array.isArray(upcomingEvents) &&
  Array.isArray(pastEvents) &&
  allEvents.length === 0 ? (
    <>
      {hasTabs && group.isManager ? <ManagerEmptyEvents /> : null}
      {hasTabs && !group.isManager && group.isMember ? (
        <MemberEmptyEvents />
      ) : null}
      <GroupDescription {...group} maxHeight="auto" />
      <ShareCard title="Inviter vos ami·es à rejoindre le groupe" />
      <GroupLocation {...group} />
    </>
  ) : (
    <>
      <GroupEventList title="Événements à venir" events={upcomingEvents} />
      <GroupEventList
        title="Événements passés"
        events={pastEvents}
        loadMore={loadMorePastEvents}
        isLoading={isLoadingPastEvents}
      />
      <GroupLocation {...group} />
      <ShareCard title="Partager le lien du groupe" />
    </>
  );
DesktopAgendaRoute.propTypes = {
  group: PropTypes.object,
  allEvents: PropTypes.arrayOf(PropTypes.object),
  upcomingEvents: PropTypes.arrayOf(PropTypes.object),
  pastEvents: PropTypes.arrayOf(PropTypes.object),
  isLoadingPastEvents: PropTypes.bool,
  loadMorePastEvents: PropTypes.func,
  hasTabs: PropTypes.bool,
};

const AgendaRoute = (props) => (
  <ResponsiveLayout
    MobileLayout={MobileAgendaRoute}
    DesktopLayout={DesktopAgendaRoute}
    {...props}
  />
);

export default AgendaRoute;
