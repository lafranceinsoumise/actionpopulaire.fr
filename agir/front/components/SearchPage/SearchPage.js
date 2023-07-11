import React, { useState, useCallback } from "react";

import { useLocation } from "react-router-dom";

import Spacer from "@agir/front/genericComponents/Spacer";
import Tabs from "@agir/front/genericComponents/Tabs";

import { useIsDesktop } from "@agir/front/genericComponents/grid";

import { HeaderSearch, InputSearch, SearchTooShort } from "./searchComponents";
import { StyledContainer } from "./styledComponents";
import SearchPageTab from "./SearchPageTab";
import SearchAndSelectField from "@agir/front/formComponents/SearchAndSelectField";

import { TABS } from "./config.js";
import { useSearchResults } from "./useSearch";
import { useFilters } from "./useFilters";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";
import { COUNTRIES } from "@agir/front/formComponents/CountryField";
import styled from "styled-components";
import style from "@agir/front/genericComponents/_variables.scss";

const StyledSelectCountry = styled.div`
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: end;
  flex-wrap: wrap;

  > label {
    flex-direction: row;
    min-width: 300px;
    width: 300px;

    span:first-child {
      margin-right: 0.5rem;
    }

    > div {
      width: 100%;

      > div > span {
        display: none !important;
      }
    }

    @media (min-width: ${style.collapse}px) {
      display: flex;
      align-items: center;

      > div:nth-child(2) {
        flex: 1;
      }
    }

    @media (max-width: ${style.collapse}px) {
      span:first-child {
        display: none;
      }
    }
  }
`;

const CancelCountry = styled.div`
  border-radius: ${style.borderRadius};
  border: 1px solid #ddd;
  margin-left: 0.5rem;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  height: 40px;
  width: 40px;
  cursor: pointer;

  :hover {
    opacity: 0.6;
  }
`;

export const SearchPage = () => {
  const isDesktop = useIsDesktop();
  const location = useLocation();
  const urlParams = new URLSearchParams(location.search);

  const [optionsCountry, setOptionsCountry] = useState(COUNTRIES);
  const [activeTabId, setActiveTabId] = useState("all");
  const [search, setSearch] = useState(urlParams.get("q") || "");
  const [_, __, filters, setFilters] = useFilters();

  const hasSearch = !!search && search.length >= 3;
  const activeTab = TABS[activeTabId];

  const [groups, events, errors, isLoading] = useSearchResults(
    search,
    activeTab?.searchType,
    filters,
  );

  const handleSearch = (e) => {
    setSearch(e.target.value);
  };
  const applyFilter = (key, value) => {
    setFilters((filters) => ({ ...filters, [key]: value }));
  };
  const resetFilters = () => {
    Object.keys(filters).length > 0 && setFilters({});
  };
  const onTabChange = (tabId) => {
    setActiveTabId(tabId);
    resetFilters();
  };

  const handleChangeCountry = useCallback((country) => {
    setFilters((filters) => ({ ...filters, country }));
    setOptionsCountry(COUNTRIES);
  }, []);

  const handleSearchCountry = useCallback(async (q) => {
    const countries = await new Promise((resolve) => {
      if (!q) {
        setOptionsCountry(COUNTRIES);
        resolve(COUNTRIES);
      } else {
        const filteredContries = COUNTRIES.filter((option) => {
          return option.label.toLowerCase().includes(q.toLowerCase());
        });
        setOptionsCountry(filteredContries);
        resolve(filteredContries);
      }
    });
    return countries;
  }, []);

  return (
    <StyledContainer>
      <HeaderSearch querySearch={search} mapRoute={activeTab.mapRoute} />

      {!isDesktop && (
        <InputSearch
          inputSearch={search}
          updateSearch={handleSearch}
          placeholder={activeTab.searchPlaceholder}
        />
      )}
      <SearchTooShort search={search} />
      <Spacer size="0.5rem" />

      <StyledSelectCountry>
        <SearchAndSelectField
          label="Pays"
          name="country"
          autoComplete="country-name"
          placeholder="Pays"
          minSearchTermLength={2}
          value={filters.country}
          defaultOptions={optionsCountry}
          onChange={handleChangeCountry}
          onSearch={handleSearchCountry}
        />
        {!!filters.country && (
          <CancelCountry
            onClick={() => setFilters({ ...filters, country: "" })}
          >
            <RawFeatherIcon name="x" height="1rem" color={style.black1000} />
          </CancelCountry>
        )}
      </StyledSelectCountry>
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
        resetFilters={resetFilters}
        onTabChange={onTabChange}
      />
    </StyledContainer>
  );
};

export default SearchPage;
