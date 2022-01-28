import React, { useState, useEffect } from "react";

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
} from "./searchComponents";
import { StyledContainer, StyledFilters } from "./styledComponents";

import { getSearch } from "./api.js";
import { TABS, TABS_OPTIONS } from "./config.js";

export const useSearchResults = (search, type, filters) => {
  const [groups, setGroups] = useState([]);
  const [events, setEvents] = useState([]);
  const [errors, setErrors] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  let filtersValue = {};
  Object.entries(filters).map(([key, value]) => {
    filtersValue = { ...filtersValue, [key]: value?.value };
  });

  useEffect(async () => {
    setIsLoading(true);
    setErrors(null);
    const { data, error } = await getSearch({
      search,
      type,
      filters: filtersValue,
    });
    setIsLoading(false);
    if (error) {
      setErrors(error);
      return;
    }

    setGroups(data.groups);
    setEvents(data.events);
  }, [search, type, filters]);

  return [groups, events, errors, isLoading];
};

export const SearchPage = () => {
  const isDesktop = useIsDesktop();
  const location = useLocation();
  const urlParams = new URLSearchParams(location.search);
  const type = undefined;

  const [search, setSearch] = useState(urlParams.get("q") || "");

  const [filters, setFilters] = useState({});
  const [groups, events, errors, isLoading] = useSearchResults(
    search,
    type,
    filters
  );

  const [showFilters, setShowFilters] = useState(false);
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

  const switchFilters = () => {
    setShowFilters(!showFilters);
    setFilters({});
  };

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
      {isLoading && <Skeleton />}

      {!!search && search.length < 3 && (
        <>Rentrez au moins 3 caractères pour rechercher</>
      )}

      {!!search && search.length >= 3 && !isLoading && (
        <>
          <Spacer size="1rem" />
          {!type && (
            <Tabs
              tabs={TABS_OPTIONS}
              activeIndex={activeTab}
              onTabChange={onTabChange}
              noBorder
            />
          )}

          {(isTabEvents || isTabGroups) && (
            <div>
              <Spacer size="1rem" />
              <div style={{ textAlign: "right" }}>
                <Button small icon="filter" onClick={switchFilters}>
                  Filtrer
                </Button>
              </div>

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
