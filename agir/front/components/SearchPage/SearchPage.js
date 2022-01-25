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

import {
  GroupList,
  EventList,
  ListTitle,
  NoResults,
} from "./resultsComponents";
import { getSearch, getSearchGroup, getSearchEvent } from "./api.js";

import mapImg from "./images/Bloc_map.jpg";

import {
  optionsEventSort,
  optionsEventCategory,
  optionsEventType,
  optionsGroupSort,
  optionsGroupType,
  TAB_ALL,
  TAB_GROUPS,
  TAB_EVENTS,
  TABS_INDEX,
  DATE_ASC,
  DATE_DESC,
  ALPHA_ASC,
  ALPHA_DESC,
  EVENT_CAT_PAST,
  EVENT_CAT_FUTURE,
  EVENT_TYPE_GROUP_MEETING,
  EVENT_TYPE_PUBLIC_MEETING,
  EVENT_TYPE_PUBLIC_ACTION,
  EVENT_TYPE_OTHER,
  GROUP_TYPE_CERTIFIED,
  GROUP_TYPE_NOT_CERTIFIED,
  GROUP_LOCAL,
  GROUP_THEMATIC,
  GROUP_FONCTIONAL,
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
    {activeTab === TAB_ALL && <MapButton />}
  </StyledHeaderSearch>
);

export const SearchPage = () => {
  const { search } = useLocation();
  const urlParams = new URLSearchParams(search);

  const params = useParams();
  const type = params?.type;

  const query = urlParams.get("q") || "";
  const [isLoading, setIsLoading] = useState(false);

  const [querySearch, setQuerySearch] = useState(query);
  const [inputSearch, setInputSearch] = useState("");
  const [results, setResults] = useState(INIT_RESULTS);
  const [errors, setErrors] = useState({});
  const [activeTab, setActiveTab] = useState(
    type === "evenements"
      ? TAB_EVENTS
      : type === "groupes"
      ? TAB_GROUPS
      : TAB_ALL
  );
  const [showFilters, setShowFilters] = useState(false);
  const [groups, setGroups] = useState([]);
  const [events, setEvents] = useState([]);

  const [eventSort, setEventSort] = useState(optionsEventSort[0]);
  const [eventType, setEventType] = useState(optionsEventType[0]);
  const [eventCategory, setEventCategory] = useState(optionsEventCategory[0]);

  const [groupSort, setGroupSort] = useState(optionsGroupSort[0]);
  const [groupType, setGroupType] = useState(optionsGroupType[0]);

  const isShowMore = activeTab === TAB_ALL;

  const customSearch = async (query) => {
    if (type === "evenements") {
      return await getSearchEvent(query);
    }
    if (type === "groupes") {
      return await getSearchGroup(query);
    }
    return await getSearch(query);
  };

  useEffect(async () => {
    if (!!querySearch) {
      setIsLoading(true);
      const { data, error } = await customSearch(querySearch);
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
          case GROUP_TYPE_CERTIFIED:
            return group.isCertified;
          case GROUP_TYPE_NOT_CERTIFIED:
            return !group.isCertified;
          case GROUP_LOCAL:
            return group.type === GROUP_LOCAL;
          case GROUP_THEMATIC:
            return group.type === GROUP_THEMATIC;
          case GROUP_FONCTIONAL:
            return group.type === GROUP_FONCTIONAL;
          default:
            return true;
        }
      }) || [];

    if (isShowMore) {
      filteredGroups = filteredGroups.slice(0, 3);
    }

    // Sort by
    if (groupSort.value === ALPHA_ASC) {
      filteredGroups = filteredGroups.sort((g1, g2) =>
        g1.name.toLowerCase().localeCompare(g2.name.toLowerCase())
      );
    } else if (groupSort.value === ALPHA_DESC) {
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
          (eventCategory.value === EVENT_CAT_PAST && event.isPast) ||
          (eventCategory.value === EVENT_CAT_FUTURE && !event.isPast)
        ) {
          return false;
        }

        // Types
        switch (eventType.value) {
          case EVENT_TYPE_PUBLIC_MEETING:
            return event.subtype.type === EVENT_TYPE_PUBLIC_MEETING;
          case EVENT_TYPE_GROUP_MEETING:
            return event.subtype.type === EVENT_TYPE_GROUP_MEETING;
          case EVENT_TYPE_PUBLIC_ACTION:
            return event.subtype.type === EVENT_TYPE_PUBLIC_ACTION;
          case EVENT_TYPE_OTHER:
            return event.subtype.type === EVENT_TYPE_OTHER;
          default:
            return true;
        }
      }) || [];

    if (isShowMore) {
      filteredEvents = filteredEvents.slice(0, 10);
    }

    // Sort by
    switch (eventSort.value) {
      case ALPHA_ASC:
        filteredEvents = filteredEvents.sort((e1, e2) =>
          e1.name.toLowerCase().localeCompare(e2.name.toLowerCase())
        );
        break;
      case ALPHA_DESC:
        filteredEvents = filteredEvents.sort((e1, e2) =>
          e2.name.toLowerCase().localeCompare(e1.name.toLowerCase())
        );
        break;
      case DATE_ASC:
        filteredEvents = filteredEvents.sort(
          (e1, e2) => new Date(e1.startTime) - new Date(e2.startTime)
        );
        break;
      case DATE_DESC:
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
    setEventSort(optionsEventSort[0]);
    setEventType(optionsEventType[0]);
    setEventCategory(optionsEventCategory[0]);

    setGroupSort(optionsGroupSort[0]);
    setGroupType(optionsGroupType[0]);
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
    const { data, error } = await customSearch(inputSearch);
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

      <Hide
        over
        as="form"
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
              (activeTab === TAB_EVENTS
                ? "un événément"
                : activeTab === TAB_GROUPS
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
      </Hide>

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
              tabs={TABS_INDEX}
              activeIndex={activeTab}
              // activeTabIndex={activeTab}
              onTabChange={onTabChange}
              noBorder
            />
          )}

          {((activeTab === TAB_EVENTS && !!results.events?.length) ||
            (activeTab === TAB_GROUPS && !!results.groups?.length)) && (
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
                  {activeTab === TAB_EVENTS && (
                    <>
                      <SelectField
                        key={1}
                        label="Trier par"
                        placeholder="Date"
                        name="eventSort"
                        value={eventSort}
                        onChange={setEventSort}
                        options={optionsEventSort}
                      />
                      <SelectField
                        key={2}
                        label="Catégorie d'événement"
                        placeholder="Categories"
                        name="eventCategory"
                        value={eventCategory}
                        onChange={setEventCategory}
                        options={optionsEventCategory}
                      />
                      <SelectField
                        key={3}
                        label="Type"
                        placeholder="Types"
                        name="eventType"
                        value={eventType}
                        onChange={setEventType}
                        options={optionsEventType}
                      />
                    </>
                  )}

                  {activeTab === TAB_GROUPS && (
                    <>
                      <SelectField
                        key={1}
                        label="Trier par"
                        placeholder="Date"
                        name="groupSort"
                        value={groupSort}
                        onChange={setGroupSort}
                        options={optionsGroupSort}
                      />
                      <SelectField
                        key={2}
                        label="Type"
                        placeholder="Types"
                        name="groupType"
                        value={groupType}
                        onChange={setGroupType}
                        options={optionsGroupType}
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

          {[TAB_ALL, TAB_GROUPS].includes(activeTab) && (
            <>
              <ListTitle
                name="Groupes"
                list={groups}
                isShowMore={isShowMore}
                onShowMore={() => onTabChange(TAB_GROUPS)}
              />
              <GroupList groups={groups} />
              {activeTab === TAB_GROUPS && (
                <NoResults
                  name="groupe"
                  list={results.groups}
                  filteredList={groups}
                />
              )}
            </>
          )}

          {[TAB_ALL, TAB_EVENTS].includes(activeTab) && (
            <>
              <ListTitle
                name="Evénements"
                list={events}
                isShowMore={isShowMore}
                onShowMore={() => onTabChange(TAB_EVENTS)}
              />
              <EventList events={events} />
              {activeTab === TAB_EVENTS && (
                <NoResults
                  name="événement"
                  list={results.events}
                  filteredList={events}
                />
              )}
            </>
          )}

          {isShowMore && !results.events?.length && !results.groups?.length && (
            <>
              <Spacer size="1rem" />
              Aucun résultat lié à cette recherche
            </>
          )}
        </>
      )}
    </StyledContainer>
  );
};

export default SearchPage;
