import { useCallback, useEffect, useMemo } from "react";
import { useHistory } from "react-router-dom";
import useSWR, { useSWRInfinite } from "swr";

import logger from "@agir/lib/utils/logger";

import GROUP_PAGE_TABS from "./tabs.config.js";

const log = logger(__filename);

export const useGroupDetail = (groupPk) => {
  const { data: group } = useSWR(`/api/groupes/${groupPk}`);
  log.debug("Group data", group);

  const { data: groupSuggestions } = useSWR(
    `/api/groupes/${groupPk}/suggestions`
  );
  log.debug("Group suggestions", groupSuggestions);

  const { data: upcomingEvents } = useSWR(
    `/api/groupes/${groupPk}/evenements/a-venir`
  );
  log.debug("Group upcoming events", upcomingEvents);

  const { data: pastEventData, size, setSize, isValidating } = useSWRInfinite(
    (pageIndex) =>
      `/api/groupes/${groupPk}/evenements/passes?page=${
        pageIndex + 1
      }&page_size=3`
  );
  const pastEvents = useMemo(() => {
    let events = [];
    if (!Array.isArray(pastEventData)) {
      return events;
    }
    pastEventData.forEach(({ results }) => {
      if (Array.isArray(results)) {
        events = events.concat(results);
      }
    });
    return events;
  }, [pastEventData]);
  log.debug("Group past events", pastEvents);
  const pastEventCount = useMemo(() => {
    if (!Array.isArray(pastEventData) || !pastEventData[0]) {
      return 0;
    }
    return pastEventData[0].count;
  }, [pastEventData]);
  const loadMorePastEvents = useCallback(() => {
    setSize(size + 1);
  }, [setSize, size]);
  const isLoadingPastEvents = !pastEventData || isValidating;

  const { data: pastEventReports } = useSWR(
    `/api/groupes/${groupPk}/evenements/compte-rendus`
  );
  log.debug("Group past event reports", pastEventReports);

  return {
    group,
    groupSuggestions,
    upcomingEvents,
    pastEvents,
    pastEventCount,
    loadMorePastEvents:
      pastEventCount > pastEvents.length ? loadMorePastEvents : undefined,
    isLoadingPastEvents,
    pastEventReports,
  };
};

export const useTabs = (props, isMobile = true) => {
  const { activeTab } = props;
  const history = useHistory();

  const tabs = useMemo(
    () =>
      GROUP_PAGE_TABS.filter((tab) =>
        typeof tab.isActive === "function"
          ? tab.isActive(props, isMobile)
          : tab.isActive
      ).map((tab) => ({
        ...tab,
        to: `/groupes/${props.group.id}/${tab.slug}/`,
        goToTab: () => {
          history.push(`/groupes/${props.group.id}/${tab.slug}/`);
        },
      })),
    [history, props, isMobile]
  );

  const { active, activeIndex } = useMemo(() => {
    const result = { active: tabs[0], activeIndex: 0 };
    tabs.forEach((tab, i) => {
      if (tab.slug === activeTab) {
        result.active = tab;
        result.activeIndex = i;
      }
    });
    return result;
  }, [tabs, activeTab]);

  const handleTabChange = useCallback((tab) => {
    tab.goToTab();
  }, []);

  const handleNextTab = useCallback(() => {
    const nextIndex = Math.min(activeIndex + 1, tabs.length - 1);
    tabs[nextIndex].goToTab();
  }, [activeIndex, tabs]);

  const handlePrevTab = useCallback(() => {
    const prevIndex = Math.max(0, activeIndex - 1);
    tabs[prevIndex].goToTab();
  }, [activeIndex, tabs]);

  useEffect(() => {
    activeTab !== active.id && history.push(active.to);
  }, [history, activeTab, active.id, active.to]);

  return {
    tabs: tabs.map((tab) => ({
      ...tab,
      isActive: active.id === tab.id || undefined,
    })),
    onTabChange: handleTabChange,
    onNextTab: handleNextTab,
    onPrevTab: handlePrevTab,
    activeTab: active,
    activeTabIndex: activeIndex,
  };
};
