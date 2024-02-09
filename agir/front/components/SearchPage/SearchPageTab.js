import PropTypes from "prop-types";
import React from "react";

import PageFadeIn from "@agir/front/genericComponents/PageFadeIn";
import Skeleton from "@agir/front/genericComponents/Skeleton";
import Spacer from "@agir/front/genericComponents/Spacer";

import {
  GroupList,
  EventList,
  ListTitle,
  NoResults,
} from "./resultsComponents";
import { GroupFilters, EventFilters } from "./searchComponents";
import { StyledFilters } from "./styledComponents";

const SearchPageTab = (props) => {
  const {
    tab,
    groups,
    events,
    filters,
    applyFilter,
    onTabChange,
    isLoading,
    hasSearch,
    isDesktop,
    hasError,
  } = props;

  if (!tab) {
    return null;
  }

  return (
    <div>
      <div style={{ padding: "1.5rem 0 1rem" }}>
        {tab.hasFilters && (
          <StyledFilters>
            {tab.hasFilters === "events" && (
              <EventFilters filters={filters} setFilter={applyFilter} />
            )}
            {tab.hasFilters === "groups" && (
              <GroupFilters filters={filters} setFilter={applyFilter} />
            )}
            <Spacer size="1rem" />
          </StyledFilters>
        )}
      </div>
      <PageFadeIn ready={!isLoading} wait={<Skeleton />}>
        {hasError && <p>Une erreur est apparue&nbsp;</p>}
        {tab.hasGroups && (
          <>
            <ListTitle
              name="Groupes"
              length={tab.id === "groups" ? groups.length : 0}
              onShowMore={
                tab.id !== "groups" ? () => onTabChange("groups") : undefined
              }
            />
            {hasSearch && <NoResults name="groupe" list={groups} />}
            <GroupList groups={groups} inline={tab.hasEvents && !isDesktop} />
          </>
        )}
        {tab.hasGroups && tab.hasEvents && <Spacer size="1.5rem" />}
        {tab.hasEvents && (
          <>
            <ListTitle
              name="Événements"
              length={tab.id === "events" ? events.length : 0}
              onShowMore={
                tab.id !== "events" ? () => onTabChange("events") : undefined
              }
            />
            {hasSearch && <NoResults name="événement" list={events} />}
            <EventList events={events} />
          </>
        )}
      </PageFadeIn>
    </div>
  );
};
SearchPageTab.propTypes = {
  tab: PropTypes.object,
  groups: PropTypes.array,
  events: PropTypes.array,
  filters: PropTypes.object,
  applyFilter: PropTypes.func,
  onTabChange: PropTypes.func,
  isLoading: PropTypes.bool,
  hasSearch: PropTypes.bool,
  isDesktop: PropTypes.bool,
  hasError: PropTypes.bool,
};
export default SearchPageTab;
