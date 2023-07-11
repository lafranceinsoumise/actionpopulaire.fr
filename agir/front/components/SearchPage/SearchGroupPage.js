import React, { useState } from "react";

import { useLocation } from "react-router-dom";

import Spacer from "@agir/front/genericComponents/Spacer";
import Skeleton from "@agir/front/genericComponents/Skeleton";

import { GroupList, ListTitle, NoResults } from "./resultsComponents";
import {
  HeaderSearch,
  InputSearch,
  GroupFilters,
  SearchTooShort,
  FilterButton,
} from "./searchComponents";
import { StyledContainer, StyledFilters } from "./styledComponents";
import { useSearchResults } from "./useSearch";
import { useFilters } from "./useFilters";

export const SearchGroupPage = () => {
  const location = useLocation();
  const urlParams = new URLSearchParams(location.search);
  const type = "groups";
  const [search, setSearch] = useState(urlParams.get("q") || "");

  const [showFilters, _, filters, setFilters, switchFilters] = useFilters();

  const [groups, __, errors, isLoading] = useSearchResults(
    search,
    type,
    filters,
  );

  return (
    <StyledContainer>
      <HeaderSearch querySearch={search} mapRoute="groupMap" />

      <InputSearch
        inputSearch={search}
        updateSearch={(e) => setSearch(e.target.value)}
        placeholder="Rechercher un groupe"
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
                <GroupFilters
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

          <ListTitle name="Groupes" length={groups.length} />
          <GroupList groups={groups} />
          <NoResults name="groupe" list={groups} />
        </>
      )}
    </StyledContainer>
  );
};

export default SearchGroupPage;
