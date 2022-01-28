import React, { useState } from "react";

import { useLocation } from "react-router-dom";

import Button from "@agir/front/genericComponents/Button";
import Spacer from "@agir/front/genericComponents/Spacer";
import Skeleton from "@agir/front/genericComponents/Skeleton";

import { EventList, ListTitle, NoResults } from "./resultsComponents";
import { HeaderSearch, InputSearch, EventFilters } from "./searchComponents";
import { StyledContainer, StyledFilters } from "./styledComponents";
import { useSearchResults } from "./useSearch";

export const SearchEventPage = () => {
  const location = useLocation();
  const urlParams = new URLSearchParams(location.search);
  const type = "events";
  const [search, setSearch] = useState(urlParams.get("q") || "");

  const [filters, setFilters] = useState({});
  const [_, events, errors, isLoading] = useSearchResults(
    search,
    type,
    filters
  );

  const [showFilters, setShowFilters] = useState(false);

  const switchFilters = () => {
    setShowFilters(!showFilters);
    setFilters({});
  };

  return (
    <StyledContainer>
      <HeaderSearch querySearch={search} />

      <InputSearch
        inputSearch={search}
        updateSearch={(e) => setSearch(e.target.value)}
        placeholder="Rechercher un événement"
      />

      {!!search && search.length < 3 && (
        <>Rentrez au moins 3 caractères pour rechercher</>
      )}

      {!!search && search.length >= 3 && !isLoading && (
        <>
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

          <Spacer size="1rem" />
          {isLoading && <Skeleton />}

          {!!errors?.length && (
            <>
              <Spacer size="1rem" />
              {errors?.name || "Une erreur est apparue ! :("}
            </>
          )}

          <ListTitle name="Evénements" list={events} />
          <EventList events={events} />
          <NoResults name="événement" list={events} />
        </>
      )}
    </StyledContainer>
  );
};

export default SearchEventPage;
