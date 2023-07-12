import React, { useState } from "react";

import { useLocation } from "react-router-dom";

import Spacer from "@agir/front/genericComponents/Spacer";
import Skeleton from "@agir/front/genericComponents/Skeleton";

import { EventList, ListTitle, NoResults } from "./resultsComponents";
import {
  HeaderSearch,
  InputSearch,
  EventFilters,
  SearchTooShort,
  FilterButton,
} from "./searchComponents";
import { StyledContainer, StyledFilters } from "./styledComponents";
import { useSearchResults } from "./useSearch";
import { useFilters } from "./useFilters";

export const SearchEventPage = () => {
  const location = useLocation();
  const urlParams = new URLSearchParams(location.search);
  const type = "events";
  const [search, setSearch] = useState(urlParams.get("q") || "");

  const [showFilters, _, filters, setFilters, switchFilters] = useFilters();

  const [__, events, errors, isLoading] = useSearchResults(
    search,
    type,
    filters,
  );

  return (
    <StyledContainer>
      <HeaderSearch querySearch={search} mapRoute="eventMap" />

      <InputSearch
        inputSearch={search}
        updateSearch={(e) => setSearch(e.target.value)}
        placeholder="Rechercher un événement"
      />

      <SearchTooShort search={search} />

      <Spacer size="1rem" />
      {isLoading && <Skeleton />}

      {search?.length >= 3 && !isLoading && (
        <>
          <div>
            <FilterButton
              showFilters={showFilters}
              switchFilters={switchFilters}
            />
            <Spacer size="1rem" />

            {showFilters && (
              <StyledFilters>
                <EventFilters
                  filters={filters}
                  setFilter={(key, value) => {
                    setFilters((filters) => ({ ...filters, [key]: value }));
                  }}
                />
                <Spacer size="1rem" />
              </StyledFilters>
            )}
          </div>

          {!!errors?.length && (
            <>
              <Spacer size="1rem" />
              {errors?.name || "Une erreur est apparue ! :("}
            </>
          )}

          <ListTitle name="Evénements" length={events.length} />
          <EventList events={events} />
          <NoResults name="événement" list={events} />
        </>
      )}
    </StyledContainer>
  );
};

export default SearchEventPage;
