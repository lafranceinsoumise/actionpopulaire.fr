import React, { useState, useEffect } from "react";

import { useLocation, useParams } from "react-router-dom";

import styled from "styled-components";
import style from "@agir/front/genericComponents/_variables.scss";

import Button from "@agir/front/genericComponents/Button";
import Spacer from "@agir/front/genericComponents/Spacer";
import Tabs from "@agir/front/genericComponents/Tabs";
import SelectField from "@agir/front/formComponents/SelectField";
import Skeleton from "@agir/front/genericComponents/Skeleton";
import { useIsDesktop } from "@agir/front/genericComponents/grid";

import {
  GroupList,
  EventList,
  ListTitle,
  NoResults,
} from "./resultsComponents";
import { HeaderSearch, InputSearch } from "./searchComponents";
import { getSearch } from "./api.js";
import { TABS, TABS_OPTIONS, OPTIONS } from "./config.js";

const StyledContainer = styled.div`
  width: 100%;
  max-width: 1100px;
  display: flex;
  flex-direction: column;
  margin: 0 auto;
  padding: 20px 50px 3rem;

  @media (max-width: ${style.collapse}px) {
    padding: 20px 12px 3rem;
  }

  h1 {
    font-size: 22px;
  }
  h2 {
    font-size: 18px;
    span {
      font-weight: normal;
    }
    display: flex;
    align-items: center;
    justify-content: space-between;
  }
`;

const StyledFilters = styled.div`
  display: flex;
  > label {
    flex: 1;
    margin-right: 10px;

    &&:last-child {
      margin-right: 0;
    }
  }

  @media (max-width: ${style.collapse}px) {
    flex-direction: column;
    > label {
      margin-right: 0;
      margin-bottom: 1rem;
    }
  }
`;

const INIT_RESULTS = {
  groups: [],
  events: [],
};

export const SearchPage = () => {
  const isDesktop = useIsDesktop();
  const { search } = useLocation();
  const urlParams = new URLSearchParams(search);
  const params = useParams();
  const type =
    params?.type === "evenements"
      ? "events"
      : params?.type === "groupes"
      ? "groups"
      : undefined;

  const query = urlParams.get("q") || "";
  const [isLoading, setIsLoading] = useState(false);
  const [querySearch, setQuerySearch] = useState(query);
  const [inputSearch, setInputSearch] = useState("");
  const [results, setResults] = useState(INIT_RESULTS);
  const [showFilters, setShowFilters] = useState(false);
  const [groups, setGroups] = useState([]);
  const [events, setEvents] = useState([]);
  const [errors, setErrors] = useState({});
  const [activeTab, setActiveTab] = useState(
    type === "events" ? TABS.EVENTS : type === "groups" ? TABS.GROUPS : TABS.ALL
  );

  const [eventSort, setEventSort] = useState(OPTIONS.EventSort[0]);
  const [eventType, setEventType] = useState(OPTIONS.EventType[0]);
  const [eventCategory, setEventCategory] = useState(OPTIONS.EventCategory[0]);
  const [groupSort, setGroupSort] = useState(OPTIONS.GroupSort[0]);
  const [groupType, setGroupType] = useState(OPTIONS.GroupType[0]);

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
  const isNoResults = !events.length && !groups.length;

  const handleSearch = async ({ search, type, filters }) => {
    setIsLoading(true);
    const { data, error } = await getSearch({ search, type, filters });
    setIsLoading(false);
    if (error) {
      setErrors(error);
    }
    return { data, error };
  };

  useEffect(async () => {
    if (!!querySearch) {
      const { data, error } = await handleSearch({ search, type });
      if (error) {
        setResults(INIT_RESULTS);
        return;
      }
      setResults(data);
    }
  }, []);

  // Filter & sort groups
  useEffect(async () => {
    const filters = {
      groupType: groupType.value,
      groupSort: groupSort.value,
    };

    const { data, error } = await handleSearch({
      search: querySearch,
      type,
      filters,
    });
    if (error) {
      setGroups([]);
      return;
    }

    if (isTabAll) {
      setGroups(data.groups.slice(0, 10));
      return;
    }
    setGroups(data.groups);
  }, [results, groupType, groupSort]);

  // Filter & sort events
  useEffect(async () => {
    const filters = {
      eventType: eventType.value,
      eventCategory: eventCategory.value,
      eventSort: eventSort.value,
    };

    const { data, error } = await handleSearch({
      search: querySearch,
      type,
      filters,
    });
    if (error) {
      setEvents([]);
      return;
    }

    if (isTabAll) {
      setEvents(data.events.slice(0, 10));
      return;
    }
    setEvents(data.events);
  }, [results, eventType, eventSort, eventCategory]);

  const updateSearch = (e) => {
    setInputSearch(e.target.value);
  };

  const onTabChange = (tab) => {
    setActiveTab(tab);
    setShowFilters(false);
    resetFilters();
  };

  const resetFilters = () => {
    setEventSort(OPTIONS.EventSort[0]);
    setEventType(OPTIONS.EventType[0]);
    setEventCategory(OPTIONS.EventCategory[0]);
    setGroupSort(OPTIONS.GroupSort[0]);
    setGroupType(OPTIONS.GroupType[0]);
  };

  const switchFilters = () => {
    setShowFilters(!showFilters);
    resetFilters();
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!inputSearch) {
      return;
    }

    const filters = {
      groupType: groupType.value,
      groupSort: groupSort.value,
      eventType: eventType.value,
      eventCategory: eventCategory.value,
      eventSort: eventSort.value,
    };

    const { data, error } = await handleSearch({
      search: inputSearch,
      type,
      filters,
    });

    resetFilters();
    setQuerySearch(inputSearch);
    if (error) {
      setResults(INIT_RESULTS);
      return;
    }
    setResults(data);
  };

  return (
    <StyledContainer>
      <HeaderSearch querySearch={querySearch} showMap={isTabAll} />

      {(!isDesktop || !!type) && (
        <InputSearch
          inputSearch={inputSearch}
          updateSearch={updateSearch}
          onSubmit={handleSubmit}
          placeholder={placeholder}
        />
      )}

      {isLoading && (
        <>
          <Spacer size="1.5rem" />
          <Skeleton />
        </>
      )}

      {!!querySearch && !isLoading && (
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
                    <>
                      <SelectField
                        key={1}
                        label="Trier par"
                        placeholder="Date"
                        name="eventSort"
                        value={eventSort}
                        onChange={setEventSort}
                        options={OPTIONS.EventSort}
                      />
                      <SelectField
                        key={2}
                        label="Catégorie d'événement"
                        placeholder="Categories"
                        name="eventCategory"
                        value={eventCategory}
                        onChange={setEventCategory}
                        options={OPTIONS.EventCategory}
                      />
                      <SelectField
                        key={3}
                        label="Type"
                        placeholder="Types"
                        name="eventType"
                        value={eventType}
                        onChange={setEventType}
                        options={OPTIONS.EventType}
                      />
                    </>
                  )}

                  {isTabGroups && (
                    <>
                      <SelectField
                        key={1}
                        label="Trier par"
                        placeholder="Date"
                        name="groupSort"
                        value={groupSort}
                        onChange={setGroupSort}
                        options={OPTIONS.GroupSort}
                      />
                      <SelectField
                        key={2}
                        label="Type"
                        placeholder="Types"
                        name="groupType"
                        value={groupType}
                        onChange={setGroupType}
                        options={OPTIONS.GroupType}
                      />
                    </>
                  )}
                  <Spacer size="1rem" />
                </StyledFilters>
              )}
            </div>
          )}

          {!!errors.length && (
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
