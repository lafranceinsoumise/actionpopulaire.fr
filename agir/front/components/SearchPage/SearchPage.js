import React, { useState } from "react";

import { useLocation } from "react-router-dom";

import Spacer from "@agir/front/genericComponents/Spacer";
import Tabs from "@agir/front/genericComponents/Tabs";

import { useIsDesktop } from "@agir/front/genericComponents/grid";

import { HeaderSearch, InputSearch, SearchTooShort } from "./searchComponents";
import { StyledContainer } from "./styledComponents";
import SearchPageTab from "./SearchPageTab";

import { TABS } from "./config.js";
import { useSearchResults } from "./useSearch";
import { useFilters } from "./useFilters";

export const SearchPage = () => {
  const isDesktop = useIsDesktop();
  const location = useLocation();
  const urlParams = new URLSearchParams(location.search);

  const [activeTabId, setActiveTabId] = useState("all");
  const [search, setSearch] = useState(urlParams.get("q") || "");
  const [_, __, filters, setFilters] = useFilters();

  const hasSearch = !!search && search.length >= 3;
  const activeTab = TABS[activeTabId];

  const [groups, events, errors, isLoading] = useSearchResults(
    search,
    activeTab?.searchType,
    filters
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
      <Spacer size="1rem" />
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
