import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import { ResponsiveLayout } from "@agir/front/genericComponents/grid";
import ShareCard from "@agir/front/genericComponents/ShareCard";
import Spacer from "@agir/front/genericComponents/Spacer";

import GroupLocation from "@agir/groups/groupPage/GroupLocation";
import GroupContactCard from "@agir/groups/groupPage/GroupContactCard";
import GroupDescription from "@agir/groups/groupPage/GroupDescription";
import GroupLinks from "@agir/groups/groupPage/GroupLinks";
import GroupFacts from "@agir/groups/groupPage/GroupFacts";
import GroupDonation from "@agir/groups/groupPage/GroupDonation";
import GroupSuggestions from "@agir/groups/groupPage/GroupSuggestions";
import GroupOrders from "@agir/groups/groupPage/GroupOrders";

import { PromoMessage } from "@agir/groups/messages/PromoMessageModal";

import { AgendaRoutePreview, MessagesRoutePreview } from "./RoutePreviews";
import CollapsibleAnnouncementCard from "@agir/activity/common/CollapsibleAnnouncementCard";

const StyledShareCard = styled.div`
  box-shadow: rgba(0, 35, 44, 0.5) 0px 0px 1px,
    rgba(0, 35, 44, 0.08) 0px 2px 0px;

  & > * {
    box-shadow: none;
  }
`;

const MobileInfoRoute = (props) => {
  const {
    group,
    groupSuggestions,
    goToMessagesTab,
    groupSettingsLinks,
    backLink,
  } = props;

  if (!group) {
    return null;
  }

  return (
    <>
      {(group.hasUpcomingEvents || group.hasPastEvents) && (
        <AgendaRoutePreview {...props} />
      )}
      {group.hasMessages && <MessagesRoutePreview {...props} />}
      {!group.hasMessages && group.isManager && (
        <>
          <PromoMessage goToMessages onClick={goToMessagesTab} />
          <Spacer size="1.5rem" />
        </>
      )}

      <GroupContactCard
        id={group?.id}
        isMessagingEnabled={group?.isMessagingEnabled}
        contact={group?.contact}
        editLinkTo={groupSettingsLinks?.contact}
      />
      <GroupOrders {...group} />
      <GroupDescription {...group} editLinkTo={groupSettingsLinks?.general} />
      <GroupLinks {...group} editLinkTo={groupSettingsLinks?.links} />
      <GroupFacts {...group} />
      <GroupLocation {...group} groupSettingsLinks={groupSettingsLinks} />
      <GroupDonation {...group} />
      <StyledShareCard>
        <ShareCard
          url={group.routes?.details}
          title="Partager le lien du groupe"
        />
      </StyledShareCard>

      {Array.isArray(groupSuggestions) && groupSuggestions.length > 0 ? (
        <div style={{ paddingTop: "2rem" }}>
          <GroupSuggestions groups={groupSuggestions} backLink={backLink} />
        </div>
      ) : null}
    </>
  );
};

const DesktopInfoRoute = (props) => {
  const { group, goToMessagesTab, groupSettingsLinks } = props;

  if (!group) {
    return <></>;
  }

  return (
    <>
      {(group.hasUpcomingEvents || group.hasPastEvents) && (
        <AgendaRoutePreview {...props} />
      )}
      {group.hasMessages && <MessagesRoutePreview {...props} />}
      {!group.hasMessages && group.isManager && (
        <>
          <PromoMessage goToMessages onClick={goToMessagesTab} />
          <Spacer size="1.5rem" />
        </>
      )}

      {group.hasUpcomingEvents || group.hasPastEvents || group.hasMessages ? (
        <>
          <GroupLocation {...group} groupSettingsLinks={groupSettingsLinks} />
          <ShareCard
            url={group.routes?.details}
            title="Partager le lien du groupe"
          />
        </>
      ) : (
        <>
          <GroupDescription
            {...group}
            maxHeight="auto"
            outlined
            editLinkTo={groupSettingsLinks?.general}
          />
          <ShareCard
            url={group.routes?.details}
            title="Partager le lien du groupe"
          />
          <GroupLocation {...group} groupSettingsLinks={groupSettingsLinks} />
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
      details: PropTypes.string,
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
  groupSettingsLinks: PropTypes.object,
  backLink: PropTypes.oneOfType([PropTypes.string, PropTypes.object]),
};

const InfoRoute = (props) => (
  <>
    {props.group?.isBoucleDepartementale && (
      <CollapsibleAnnouncementCard slug="BouclesDepartementaleLongAnnouncement" />
    )}
    <ResponsiveLayout
      {...props}
      MobileLayout={MobileInfoRoute}
      DesktopLayout={DesktopInfoRoute}
    />
  </>
);
InfoRoute.propTypes = {
  group: PropTypes.shape({
    isBoucleDepartementale: PropTypes.bool,
  }),
};

export default InfoRoute;
