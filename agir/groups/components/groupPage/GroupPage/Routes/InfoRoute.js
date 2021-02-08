import PropTypes from "prop-types";
import React from "react";

import { ResponsiveLayout } from "@agir/front/genericComponents/grid";
import ShareCard from "@agir/front/genericComponents/ShareCard";

import GroupLocation from "@agir/groups/groupPage/GroupLocation";
import GroupContactCard from "@agir/groups/groupPage/GroupContactCard";
import GroupDescription from "@agir/groups/groupPage/GroupDescription";
import GroupLinks from "@agir/groups/groupPage/GroupLinks";
import GroupFacts from "@agir/groups/groupPage/GroupFacts";
import GroupDonation from "@agir/groups/groupPage/GroupDonation";
import GroupSuggestions from "@agir/groups/groupPage/GroupSuggestions";
import GroupOrders from "@agir/groups/groupPage/GroupOrders";

import { AgendaRoutePreview, MessagesRoutePreview } from "./RoutePreviews";

const MobileInfoRoute = (props) => {
  const { group, groupSuggestions } = props;
  return (
    <>
      {group && (group.hasUpcomingEvents || group.hasPastEvents) ? (
        <AgendaRoutePreview {...props} />
      ) : null}
      {group && group.hasMessages ? <MessagesRoutePreview {...props} /> : null}
      <GroupContactCard {...group} />
      <GroupOrders {...group} />
      <GroupDescription {...group} />
      <GroupLinks {...group} />
      <GroupFacts {...group} />
      <GroupLocation {...group} />
      {group.routes && group.routes.donations && (
        <GroupDonation url={group.routes.donations} />
      )}
      <ShareCard title="Partager le lien du groupe" />

      {Array.isArray(groupSuggestions) && groupSuggestions.length > 0 ? (
        <div style={{ paddingTop: "2rem" }}>
          <GroupSuggestions groups={groupSuggestions} />
        </div>
      ) : null}
    </>
  );
};

const DesktopInfoRoute = (props) => {
  const { group } = props;

  return (
    <>
      {group && (group.hasUpcomingEvents || group.hasPastEvents) ? (
        <AgendaRoutePreview {...props} />
      ) : null}
      {group && group.hasMessages ? <MessagesRoutePreview {...props} /> : null}
      {group &&
      (group.hasUpcomingEvents || group.hasPastEvents || group.hasMessages) ? (
        <>
          <GroupLocation {...group} />
          <ShareCard title="Partager le lien du groupe" />
        </>
      ) : (
        <>
          <GroupDescription {...group} maxHeight="auto" />
          <ShareCard title="Inviter vos ami·es à rejoindre le groupe" />
          <GroupLocation {...group} />
        </>
      )}
    </>
  );
};

MobileInfoRoute.propTypes = DesktopInfoRoute.propTypes = {
  user: PropTypes.object,
  group: PropTypes.shape({
    isMember: PropTypes.bool,
    isManager: PropTypes.bool,
    hasPastEvents: PropTypes.bool,
    hasUpcomingEvents: PropTypes.bool,
    hasMessages: PropTypes.bool,
    routes: PropTypes.shape({
      donations: PropTypes.string,
    }),
  }),
  upcomingEvents: PropTypes.arrayOf(PropTypes.object),
  pastEvents: PropTypes.arrayOf(PropTypes.object),
  messages: PropTypes.arrayOf(PropTypes.object),
  goToAgendaTab: PropTypes.func,
  goToMessagesTab: PropTypes.func,
  onClickMessage: PropTypes.func,
  isLoadingMessages: PropTypes.bool,
};

const InfoRoute = (props) => (
  <ResponsiveLayout
    {...props}
    MobileLayout={MobileInfoRoute}
    DesktopLayout={DesktopInfoRoute}
  />
);

export default InfoRoute;
