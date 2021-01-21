import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

import ShareCard from "@agir/front/genericComponents/ShareCard";

import GroupLocation from "@agir/groups/groupPage/GroupLocation";
import GroupContactCard from "@agir/groups/groupPage/GroupContactCard";
import GroupDescription from "@agir/groups/groupPage/GroupDescription";
import GroupLinks from "@agir/groups/groupPage/GroupLinks";
import GroupFacts from "@agir/groups/groupPage/GroupFacts";
import GroupDonation from "@agir/groups/groupPage/GroupDonation";
import GroupSuggestions from "@agir/groups/groupPage/GroupSuggestions";
import GroupEventList from "@agir/groups/groupPage/GroupEventList";

const Agenda = styled.div`
  margin: 0;
  padding: 1.5rem 1rem;
  height: 316px;
  background: ${style.black25};

  & > h3 {
    margin-top: 0;
    margin-bottom: 1rem;
  }
`;

const InfoRoute = ({
  upcomingEvents,
  goToAgendaTab,
  group,
  groupSuggestions,
}) => (
  <>
    {Array.isArray(upcomingEvents) && upcomingEvents.length > 0 ? (
      <Agenda>
        <h3>Agenda</h3>
        <GroupEventList
          events={[upcomingEvents[0]]}
          loadMore={goToAgendaTab}
          loadMoreLabel="Voir tout l'agenda"
        />
      </Agenda>
    ) : null}

    <GroupContactCard {...group} />
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
InfoRoute.propTypes = {
  group: PropTypes.shape({
    isMember: PropTypes.bool,
    isManager: PropTypes.bool,
    routes: PropTypes.shape({
      donations: PropTypes.string,
    }),
  }),
  upcomingEvents: PropTypes.arrayOf(PropTypes.object),
  groupSuggestions: PropTypes.arrayOf(PropTypes.object),
  goToAgendaTab: PropTypes.func,
};

export default InfoRoute;
