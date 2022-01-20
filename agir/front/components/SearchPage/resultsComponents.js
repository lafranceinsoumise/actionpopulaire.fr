import PropTypes from "prop-types";
import React from "react";

import { Interval } from "luxon";
import styled from "styled-components";

import Button from "@agir/front/genericComponents/Button";
import Spacer from "@agir/front/genericComponents/Spacer";
import { ResponsiveLayout } from "@agir/front/genericComponents/grid";
import EventCard from "@agir/front/genericComponents/EventCard";
import GroupSuggestionCard from "@agir/groups/groupPage/GroupSuggestionCard";
import { GroupSuggestionCarousel } from "@agir/groups/groupPage/GroupSuggestions";

import { TAB_ALL, TAB_GROUPS, TAB_EVENTS } from "./SearchPage";

const StyledGroupsDesktop = styled.div`
  display: flex;
  flex-flow: wrap;
  justify-content: space-between;

  > div {
    width: 100%;
    max-width: 310px;
    margin-bottom: 10px;
  }
`;

const GroupsDesktop = ({ groups }) => (
  <StyledGroupsDesktop>
    {groups.map((group) => (
      <div>
        <GroupSuggestionCard key={group.id} {...group} />
      </div>
    ))}
  </StyledGroupsDesktop>
);

export const GroupList = ({ results, groups, activeTab, setActiveTab }) => {
  if (![TAB_ALL, TAB_GROUPS].includes(activeTab)) {
    return null;
  }

  return (
    <>
      {!!groups?.length && (
        <h2>
          <div>
            Groupes <span>{groups.length}</span>
          </div>
          {activeTab === TAB_ALL && (
            <Button
              color="primary"
              small
              onClick={() => setActiveTab(TAB_GROUPS)}
            >
              Voir tout
            </Button>
          )}
        </h2>
      )}
      <div>
        <ResponsiveLayout
          MobileLayout={GroupSuggestionCarousel}
          DesktopLayout={GroupsDesktop}
          groups={groups}
        />
      </div>
      {activeTab === TAB_GROUPS && !results.groups?.length && (
        <>
          <Spacer size="1rem" />
          Aucun groupe lié à cette recherche
        </>
      )}
    </>
  );
};
GroupList.PropTypes = {
  groups: PropTypes.array,
  results: PropTypes.shape({
    groups: PropTypes.array,
    events: PropTypes.array,
  }),
  activeTab: PropTypes.number,
  setActiveTab: PropTypes.func,
};

export const EventList = ({ results, events, activeTab, setActiveTab }) => {
  if (![TAB_ALL, TAB_EVENTS].includes(activeTab)) {
    return null;
  }

  return (
    <>
      {!!events.length && (
        <h2>
          <div>
            Evénements <span>{events.length}</span>
          </div>
          {activeTab === TAB_ALL && (
            <Button
              color="primary"
              small
              onClick={() => setActiveTab(TAB_EVENTS)}
            >
              Voir tout
            </Button>
          )}
        </h2>
      )}
      {events.map((event) => {
        return (
          <>
            <EventCard
              key={event.id}
              {...event}
              schedule={Interval.fromISO(`${event.startTime}/${event.endTime}`)}
            />
            <Spacer size="1rem" />
          </>
        );
      })}
      {activeTab === TAB_EVENTS && !results.events?.length && (
        <>
          <Spacer size="1rem" />
          Aucun événement lié à cette recherche
        </>
      )}
    </>
  );
};
EventList.PropTypes = {
  events: PropTypes.array,
  results: PropTypes.shape({
    groups: PropTypes.array,
    events: PropTypes.array,
  }),
  activeTab: PropTypes.number,
  setActiveTab: PropTypes.func,
};
