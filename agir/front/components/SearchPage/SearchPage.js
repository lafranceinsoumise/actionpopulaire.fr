import React, { useCallback, useState } from "react";
import styled from "styled-components";

import Spacer from "@agir/front/genericComponents/Spacer";
import Tabs from "@agir/front/genericComponents/Tabs";

import { useLocationState } from "@agir/front/app/hooks";
import { useIsDesktop } from "@agir/front/genericComponents/grid";

import CommuneField from "@agir/front/formComponents/CommuneField";
import CountryField from "@agir/front/formComponents/CountryField.js";
import SearchPageTab from "./SearchPageTab";
import { HeaderSearch, InputSearch, SearchTooShort } from "./searchComponents";
import { StyledContainer } from "./styledComponents";

import { COUNTRIES } from "@agir/front/formComponents/CountryField";
import { TABS } from "./config.js";
import { useFilters } from "./useFilters";
import { useSearchResults } from "./useSearch";

const StyledLocationFields = styled.div`
  width: 100%;
  padding: 1rem 0;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 0.5rem;

  & > * {
    width: 475px;
    display: flex;
    flex-flow: row nowrap;
    justify-content: flex-end;
    align-items: center;
    gap: 0.75rem;

    @media (max-width: ${(props) => props.theme.collapse}px) {
      width: 100%;
    }

    & > span {
      width: 120px;
      text-align: right;
      font-size: 0.875rem;

      @media (max-width: ${(props) => props.theme.collapse}px) {
        white-space: nowrap;
        width: max-content;
      }

      @media (max-width: 400px) {
        display: none;
      }
    }

    & > span + * {
      flex: 1 1 100%;
    }
  }
`;

export const SearchPage = () => {
  const isDesktop = useIsDesktop();

  const [activeTabId, setActiveTabId] = useState("all");
  const [search, setSearch] = useLocationState("q");
  const [_, __, filters, setFilters] = useFilters();

  const hasSearch = !!search && search.length >= 3;
  const activeTab = TABS[activeTabId];

  const [groups, events, errors, isLoading] = useSearchResults(
    search,
    activeTab?.searchType,
    filters,
  );

  const handleSearch = useCallback(
    (e) => {
      setSearch(e.target.value);
    },
    [setSearch],
  );

  const applyFilter = useCallback(
    (key, value) => {
      setFilters((filters) => ({ ...filters, [key]: value }));
    },
    [setFilters],
  );

  const onTabChange = useCallback(
    (tabId) => {
      setActiveTabId(tabId);
      setFilters((filters) => ({
        commune: filters.commune,
        country: filters.country,
      }));
    },
    [setActiveTabId, setFilters],
  );

  const handleChangeCountry = useCallback(
    (country) => {
      setFilters((filters) => ({
        ...filters,
        country: country,
        commune: null,
      }));
    },
    [setFilters],
  );

  const handleChangeCommune = useCallback(
    (commune) => {
      setFilters((filters) => ({
        ...filters,
        commune,
        country: commune ? COUNTRIES[0].value : filters.country,
      }));
    },
    [setFilters],
  );

  return (
    <StyledContainer>
      <HeaderSearch querySearch={search} mapRoute={activeTab.mapRoute} />
      <InputSearch
        inputSearch={search}
        updateSearch={handleSearch}
        placeholder={activeTab.searchPlaceholder}
      />
      <SearchTooShort search={search} />
      <Spacer size="0.5rem" />
      <StyledLocationFields>
        <CommuneField
          label="Commune"
          name="commune"
          placeholder="Chercher par nom, département..."
          value={filters.commune || null}
          onChange={handleChangeCommune}
          types={["COM", "ARM"]}
          searchIcon={false}
        />
        <CountryField
          isClearable
          label="Pays"
          name="country"
          autoComplete="country-name"
          placeholder="Chercher par nom"
          value={filters.country}
          onChange={handleChangeCountry}
        />
      </StyledLocationFields>
      <Spacer size="0.5rem" />

      <Tabs
        tabs={Object.values(TABS)}
        activeIndex={Object.keys(TABS).findIndex((key) => key === activeTabId)}
        onTabChange={onTabChange}
        noBorder
      />
      <SearchPageTab
        tab={activeTab}
        isLoading={isLoading}
        hasSearch={hasSearch}
        isDesktop={isDesktop}
        groups={groups}
        events={events}
        filters={filters}
        hasError={errors?.length > 0}
        applyFilter={applyFilter}
        onTabChange={onTabChange}
      />
    </StyledContainer>
  );
};

export default SearchPage;
