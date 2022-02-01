import React, { useState } from "react";

import { useLocation } from "react-router-dom";

import Button from "@agir/front/genericComponents/Button";
import Spacer from "@agir/front/genericComponents/Spacer";
import Tabs from "@agir/front/genericComponents/Tabs";
import Skeleton from "@agir/front/genericComponents/Skeleton";
import { useIsDesktop } from "@agir/front/genericComponents/grid";

import {
  GroupList,
  EventList,
  ListTitle,
  NoResults,
} from "./resultsComponents";
import {
  HeaderSearch,
  InputSearch,
  GroupFilters,
  EventFilters,
  SearchTooShort,
  FilterButton,
} from "./searchComponents";
import { StyledContainer, StyledFilters } from "./styledComponents";

import { TABS, TABS_OPTIONS } from "./config.js";
import { useSearchResults } from "./useSearch";
import { useFilters } from "./useFilters";

export const SearchPage = () => {
  const isDesktop = useIsDesktop();
  const location = useLocation();
  const urlParams = new URLSearchParams(location.search);
  const type = undefined;

  const [search, setSearch] = useState(urlParams.get("q") || "");

  const [showFilters, setShowFilters, filters, setFilters, switchFilters] =
    useFilters();
  const [groups, events, errors, isLoading] = useSearchResults(
    search,
    isTabEvents ? "events" : isTabGroups ? "groups" : undefined,
    filters
  );

  const [activeTab, setActiveTab] = useState(TABS.ALL);

  const isTabAll = activeTab === TABS.ALL;
  const isTabGroups = activeTab === TABS.GROUPS;
  const isTabEvents = activeTab === TABS.EVENTS;
  const placeholder =
    "Rechercher " +
    (isTabEvents
      ? "un événément"
      : isTabGroups
      ? "un groupe"
      : "sur Action Populaire");
  const isNoResults = !events?.length && !groups?.length;

  const onTabChange = (tab) => {
    setActiveTab(tab);
    setShowFilters(false);
    setFilters({});
  };

  if (search?.length <= 3) {
    return (
      <StyledContainer>
        <HeaderSearch querySearch={search} showMap={isTabAll} />
        {!isDesktop && (
          <InputSearch
            inputSearch={search}
            updateSearch={(e) => setSearch(e.target.value)}
            placeholder={placeholder}
          />
        )}
        <SearchTooShort search={search} />
      </StyledContainer>
    );
  }

  return (
    <StyledContainer>
      <HeaderSearch querySearch={search} showMap={isTabAll} />

      {(!isDesktop || !!type) && (
        <InputSearch
          inputSearch={search}
          updateSearch={(e) => setSearch(e.target.value)}
          placeholder={placeholder}
        />
      )}

      <Spacer size="1rem" />
      <Tabs
        tabs={TABS_OPTIONS}
        activeIndex={activeTab}
        onTabChange={onTabChange}
        noBorder
      />

      {!isTabAll && (
        <div>
          <FilterButton
            showFilters={showFilters}
            switchFilters={switchFilters}
          />
          <Spacer size="1rem" />

          {showFilters && (
            <StyledFilters>
              {isTabEvents && (
                <EventFilters
                  filters={filters}
                  setFilter={(key, value) => {
                    setFilters((filters) => ({ ...filters, [key]: value }));
                  }}
                />
              )}
              {isTabGroups && (
                <GroupFilters
                  filters={filters}
                  setFilter={(key, value) => {
                    setFilters((filters) => ({ ...filters, [key]: value }));
                  }}
                />
              )}
              <Spacer size="1rem" />
            </StyledFilters>
          )}
        </div>
      )}

      <Spacer size="1rem" />
      {isLoading && <Skeleton />}

      {search?.length >= 3 && !isLoading && (
        <>
          {!!errors?.length && (
            <>
              <Spacer size="1rem" />
              {errors?.name || "Une erreur est apparue ! :("}
            </>
          )}

          {(isTabAll || isTabGroups) && (
            <>
              <ListTitle
                name="Groupes"
                list={groups}
                isShowMore={isTabAll}
                onShowMore={() => onTabChange(TABS.GROUPS)}
              />
              <GroupList groups={groups} />
              {isTabGroups && <NoResults name="groupe" list={groups} />}
            </>
          )}

          {(isTabAll || isTabEvents) && (
            <>
              <ListTitle
                name="Evénements"
                list={events}
                isShowMore={isTabAll}
                onShowMore={() => onTabChange(TABS.EVENTS)}
              />
              <EventList events={events} />
              {isTabEvents && <NoResults name="événement" list={events} />}
            </>
          )}

          {isTabAll && isNoResults && <NoResults name="résultat" list={[]} />}
        </>
      )}
    </StyledContainer>
  );
};

export default SearchPage;
