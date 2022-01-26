import React, { useState, useEffect } from "react";

import { useLocation, useParams } from "react-router-dom";

import styled from "styled-components";
import style from "@agir/front/genericComponents/_variables.scss";

import Button from "@agir/front/genericComponents/Button";
import Link from "@agir/front/app/Link";
import Spacer from "@agir/front/genericComponents/Spacer";
import { Hide } from "@agir/front/genericComponents/grid";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";
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
import { getSearch } from "./api.js";

import mapImg from "./images/Bloc_map.jpg";

import {
  TABS,
  TABS_OPTIONS,
  OPTIONS,
  SORTERS,
  EVENT_TIMES,
  EVENT_TYPES,
  GROUP_TYPES,
} from "./config.js";

const SearchBarWrapper = styled.div`
  border-radius: 4px;
  border: 1px solid #dddddd;
  position: relative;
  display: flex;
  align-items: center;
  flex: 1;
  height: 50px;

  @media (max-width: ${style.collapse}px) {
    height: 40px;
  }
`;

const SearchBarInput = styled.input`
  border: none;
  max-width: 100%;
  width: 90%;
  height: 100%;
  margin-left: 2.5rem;
  padding-left: 0.5rem;
  display: inline-flex;
  flex: 1;

  ::placeholder {
    color: ${style.black500};
    font-weight: 400;
    text-overflow: ellipsis;
    font-size: 0.875rem;
    opacity: 1;
  }
`;

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

const StyledLink = styled(Link)``;

const StyledMapButton = styled.div`
  max-width: 370px;
  width: 100%;
  overflow: hidden;
  border: 1px solid #ddd;
  border-radius: ${style.borderRadius};
  cursor: pointer;
  margin-bottom: 0.5rem;

  ${StyledLink} > div:first-child {
    height: 80px;
    background-image: url("${mapImg}");
    background-size: cover;
  }
  ${StyledLink} > div:nth-child(2) {
    height: 40px;
    display: flex;
    justify-content: center;
    align-items: center;
    color: ${style.black1000};
  }
`;

const StyledHeaderSearch = styled.div`
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.5rem;

  > div:first-child {
    max-width: 480px;
  }
  h1 {
    margin: 0;
  }

  @media (max-width: ${style.collapse}px) {
    flex-direction: column-reverse;
    h1 {
      font-size: 20px;
    }
  }
`;

const INIT_RESULTS = {
  count: 0,
  groups: [],
  events: [],
};

const MapButton = () => (
  <StyledMapButton>
    <StyledLink route="eventMap">
      <div />
      <div>Voir la carte</div>
    </StyledLink>
  </StyledMapButton>
);

const HeaderSearch = ({ querySearch, activeTab }) => (
  <StyledHeaderSearch>
    <div>
      <h1>
        {!querySearch ? (
          "Rechercher"
        ) : (
          <Hide under>Recherche : "{querySearch}"</Hide>
        )}
      </h1>
      <Hide under as="div" style={{ marginTop: "0.5rem" }}>
        Recherchez des événements et des groupes d'actions par nom, ville, code
        postal...
      </Hide>
    </div>
    {activeTab === TABS.ALL && <MapButton />}
  </StyledHeaderSearch>
);

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
  const [errors, setErrors] = useState({});
  const [activeTab, setActiveTab] = useState(
    type === "events" ? TABS.EVENTS : type === "groups" ? TABS.GROUPS : TABS.ALL
  );
  const [showFilters, setShowFilters] = useState(false);
  const [groups, setGroups] = useState([]);
  const [events, setEvents] = useState([]);

  const [eventSort, setEventSort] = useState(OPTIONS.EventSort[0]);
  const [eventType, setEventType] = useState(OPTIONS.EventType[0]);
  const [eventCategory, setEventCategory] = useState(OPTIONS.EventCategory[0]);

  const [groupSort, setGroupSort] = useState(OPTIONS.GroupSort[0]);
  const [groupType, setGroupType] = useState(OPTIONS.GroupType[0]);

  const isShowMore = activeTab === TABS.ALL;

  useEffect(async () => {
    if (!!querySearch) {
      setIsLoading(true);
      const { data, error } = await getSearch({ search: querySearch, type });
      setIsLoading(false);
      if (error) {
        setErrors(error);
        setResults(INIT_RESULTS);
        return;
      }
      setResults(data);
    }
  }, []);

  // Filter & sort groups
  useEffect(() => {
    // Filters
    let filteredGroups =
      results.groups?.filter((group) => {
        switch (groupType.value) {
          case GROUP_TYPES.CERTIFIED:
            return group.isCertified;
          case GROUP_TYPES.NOT_CERTIFIED:
            return !group.isCertified;
          case GROUP_TYPES.LOCAL:
            return group.type === GROUP_TYPES.LOCAL;
          case GROUP_TYPES.THEMATIC:
            return group.type === GROUP_TYPES.THEMATIC;
          case GROUP_TYPES.FONCTIONAL:
            return group.type === GROUP_TYPES.FONCTIONAL;
          default:
            return true;
        }
      }) || [];

    if (isShowMore) {
      filteredGroups = filteredGroups.slice(0, 3);
    }

    // Sort by
    if (groupSort.value === SORTERS.ALPHA_ASC) {
      filteredGroups = filteredGroups.sort((g1, g2) =>
        g1.name.toLowerCase().localeCompare(g2.name.toLowerCase())
      );
    } else if (groupSort.value === SORTERS.ALPHA_DESC) {
      filteredGroups = filteredGroups.sort((g1, g2) =>
        g2.name.toLowerCase().localeCompare(g1.name.toLowerCase())
      );
    }

    setGroups(filteredGroups);
  }, [results, groupType, groupSort]);

  // Filter & sort events
  useEffect(() => {
    // Filters
    let filteredEvents =
      results.events?.filter((event) => {
        // Categories
        if (
          (eventCategory.value === EVENT_TIMES.PAST && event.isPast) ||
          (eventCategory.value === EVENT_TIMES.FUTURE && !event.isPast)
        ) {
          return false;
        }

        // Types
        switch (eventType.value) {
          case EVENT_TYPES.PUBLIC_MEETING:
            return event.subtype.type === EVENT_TYPES.PUBLIC_MEETING;
          case EVENT_TYPES.GROUP_MEETING:
            return event.subtype.type === EVENT_TYPES.GROUP_MEETING;
          case EVENT_TYPES.PUBLIC_ACTION:
            return event.subtype.type === EVENT_TYPES.PUBLIC_ACTION;
          case EVENT_TYPES.OTHER:
            return event.subtype.type === EVENT_TYPES.OTHER;
          default:
            return true;
        }
      }) || [];

    if (isShowMore) {
      filteredEvents = filteredEvents.slice(0, 10);
    }

    // Sort by
    switch (eventSort.value) {
      case SORTERS.ALPHA_ASC:
        filteredEvents = filteredEvents.sort((e1, e2) =>
          e1.name.toLowerCase().localeCompare(e2.name.toLowerCase())
        );
        break;
      case SORTERS.ALPHA_DESC:
        filteredEvents = filteredEvents.sort((e1, e2) =>
          e2.name.toLowerCase().localeCompare(e1.name.toLowerCase())
        );
        break;
      case SORTERS.DATE_ASC:
        filteredEvents = filteredEvents.sort(
          (e1, e2) => new Date(e1.startTime) - new Date(e2.startTime)
        );
        break;
      case SORTERS.DATE_DESC:
        filteredEvents = filteredEvents.sort(
          (e1, e2) => new Date(e2.startTime) - new Date(e1.startTime)
        );
        break;
      default:
        break;
    }

    setEvents(filteredEvents);
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
    setErrors({});
    setIsLoading(true);
    const { data, error } = await getSearch({ search: inputSearch, type });
    setIsLoading(false);
    resetFilters();
    setQuerySearch(inputSearch);
    if (error) {
      setErrors(error);
      setResults(INIT_RESULTS);
      return;
    }
    setResults(data);
  };

  return (
    <StyledContainer>
      <HeaderSearch querySearch={querySearch} activeTab={activeTab} />

      {(!isDesktop || !!type) && (
        <form
          onSubmit={handleSubmit}
          style={{ display: "flex" }}
          autoComplete="off"
        >
          <SearchBarWrapper>
            <RawFeatherIcon
              name="search"
              width="1rem"
              height="1rem"
              stroke-width={1.33}
              style={{ position: "absolute", left: "1rem" }}
            />
            <SearchBarInput
              required
              placeholder={
                "Rechercher " +
                (activeTab === TABS.EVENTS
                  ? "un événément"
                  : activeTab === TABS.GROUPS
                  ? "un groupe"
                  : "sur Action Populaire")
              }
              type="text"
              name="q"
              value={inputSearch}
              onChange={updateSearch}
              autoComplete="off"
            />
          </SearchBarWrapper>
          <Hide under>
            <Button
              color="primary"
              onClick={handleSubmit}
              style={{ marginLeft: "1rem" }}
              disabled={isLoading}
            >
              Rechercher
            </Button>
          </Hide>
        </form>
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

          {((activeTab === TABS.EVENTS && !!results.events?.length) ||
            (activeTab === TABS.GROUPS && !!results.groups?.length)) && (
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
                  {activeTab === TABS.EVENTS && (
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

                  {activeTab === TABS.GROUPS && (
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

          {[TABS.ALL, TABS.GROUPS].includes(activeTab) && (
            <>
              <ListTitle
                name="Groupes"
                list={groups}
                isShowMore={isShowMore}
                onShowMore={() => onTabChange(TABS.GROUPS)}
              />
              <GroupList groups={groups} />
              {activeTab === TABS.GROUPS && (
                <NoResults
                  name="groupe"
                  list={results.groups}
                  filteredList={groups}
                />
              )}
            </>
          )}

          {[TABS.ALL, TABS.EVENTS].includes(activeTab) && (
            <>
              <ListTitle
                name="Evénements"
                list={events}
                isShowMore={isShowMore}
                onShowMore={() => onTabChange(TABS.EVENTS)}
              />
              <EventList events={events} />
              {activeTab === TABS.EVENTS && (
                <NoResults
                  name="événement"
                  list={results.events}
                  filteredList={events}
                />
              )}
            </>
          )}

          {isShowMore && !results.events?.length && !results.groups?.length && (
            <NoResults name="résultat" list={[]} filteredList={[]} />
          )}
        </>
      )}
    </StyledContainer>
  );
};

export default SearchPage;
