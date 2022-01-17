import React, { useState } from "react";
import { useRouteMatch } from "react-router-dom";
import { Interval } from "luxon";

import styled from "styled-components";
import style from "@agir/front/genericComponents/_variables.scss";

import Button from "@agir/front/genericComponents/Button";
import Spacer from "@agir/front/genericComponents/Spacer";
import Tabs from "@agir/front/genericComponents/Tabs";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";

import { routeConfig } from "@agir/front/app/routes.config";
import EventCard from "@agir/front/genericComponents/EventCard";
import GroupCard from "@agir/groups/groupComponents/GroupCard";

import { getSearch } from "./api.js";

const tabs = [
  { id: "all", label: "Tout" },
  { id: "events", label: "Événements" },
  { id: "groups", label: "Groupes" },
];

const SearchBarWrapper = styled.div`
  border-radius: 4px;
  border: 1px solid #dddddd;
  height: 3rem;

  position: relative;
  display: flex;
  align-items: center;
`;

const SearchBarInput = styled.input`
  border: none;
  max-width: 100%;
  width: 90%;
  height: 2.5rem;
  margin-left: 2.5rem;
  padding-left: 0.5rem;

  ::placeholder {
    color: ${style.black500};
    font-weight: 400;
    text-overflow: ellipsis;
    font-size: 0.875rem;
    opacity: 1;
  }
`;

const INIT_RESULTS = {
  count: 0,
  groups: [],
  events: [],
};

export const SearchPage = () => {
  const groupURL = routeConfig.search.getLink();
  const isRouteMatch = useRouteMatch(groupURL);
  // console.log("is route match : ", isRouteMatch)

  const [search, setSearch] = useState("");
  const [results, setResults] = useState(INIT_RESULTS);

  const updateSearch = (e) => {
    setSearch(e.target.value);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const { data, error } = await getSearch(search);
    console.log("res data ", data);

    setResults(data);
  };

  return (
    <>
      <h2>Rechercher</h2>
      <Spacer size="1rem" />
      <form onSubmit={handleSubmit}>
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
            placeholder="Rechercher sur Action Populaire"
            type="text"
            name="q"
            value={search}
            onChange={updateSearch}
          />
        </SearchBarWrapper>
        <Button color="primary" onClick={handleSubmit}>
          Rechercher
        </Button>
      </form>

      <Spacer size="0.5rem" />
      <Button small link route="eventMap" icon="filter">
        Filtrer
      </Button>
      <Spacer size="1rem" />

      <Tabs tabs={tabs} isBorder />
      <Spacer size="1rem" />

      {results.groups?.map((group) => (
        <>
          <GroupCard key={group.id} {...group} />
          <Spacer size="1rem" />
        </>
      ))}
      {results.events?.map((event) => (
        <>
          <EventCard
            key={event.id}
            {...event}
            schedule={Interval.fromISO(`${event.startTime}/${event.endTime}`)}
          />
          <Spacer size="1rem" />
        </>
      ))}
    </>
  );
};

export default SearchPage;
