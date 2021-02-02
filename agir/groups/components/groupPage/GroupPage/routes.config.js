import { useCallback, useEffect, useMemo } from "react";
import { useHistory, useLocation } from "react-router-dom";
import { RouteConfig } from "@agir/front/app/routes.config";

const routeConfig = {
  messages: {
    id: "messages",
    pathname: "/groupes/:groupPk/discussion/",
    label: "Discussion",
    hasTab: true,
    hasRoute: (group) =>
      group.isManager || (group.isMember && group.hasMessages),
  },
  info: {
    id: "info",
    pathname: "/groupes/:groupPk/presentation/",
    label: "Présentation",
    hasTab: true,
    hasRoute: (_, isMobile) => !!isMobile,
  },
  agenda: {
    id: "agenda",
    pathname: "/groupes/:groupPk/agenda/",
    label: "Agenda",
    hasTab: true,
    hasRoute: (group, isMobile) =>
      !isMobile ||
      group.isMember ||
      group.hasUpcomingEvents ||
      group.hasPastEvents,
  },
  reports: {
    id: "reports",
    pathname: "/groupes/:groupPk/comptes-rendus/",
    label: "Comptes-rendus",
    hasTab: true,
    hasRoute: (group) =>
      group.isManager || (group.isMember && group.hasPastEventReports),
  },
};

export const useTabs = (props, isMobile = true) => {
  const history = useHistory();
  const location = useLocation();

  const { group } = props;

  const routes = useMemo(
    () =>
      Object.values(routeConfig)
        .filter((route) =>
          typeof route.hasRoute === "function"
            ? route.hasRoute(group, isMobile)
            : route.hasRoute
        )
        .map(
          (route) =>
            new RouteConfig({
              ...route,
              params: { groupPk: group.id },
            })
        ),
    [group, isMobile]
  );

  const tabs = useMemo(() => routes.filter((route) => route.hasTab), [routes]);

  const { activeRoute, shouldRedirect } = useMemo(() => {
    const result = {
      activeRoute: tabs[0],
      shouldRedirect: true,
    };
    routes.forEach((route) => {
      if (route.match(location.pathname)) {
        result.activeRoute = route;
        result.shouldRedirect = false;
      }
    });
    return result;
  }, [tabs, routes, location.pathname]);

  const activeTabIndex = useMemo(() => {
    for (let i = 0; tabs[i]; i++) {
      if (activeRoute === tabs[i]) {
        return i;
      }
    }
  }, [tabs, activeRoute]);

  const handleTabChange = useCallback(
    (route, params) => {
      route && route.getLink && history.push(route.getLink(params));
    },
    [history]
  );

  const handleNextTab = useCallback(() => {
    const nextIndex = Math.min(activeTabIndex + 1, tabs.length - 1);
    handleTabChange(tabs[nextIndex]);
  }, [handleTabChange, activeTabIndex, tabs]);

  const handlePrevTab = useCallback(() => {
    const prevIndex = Math.max(0, activeTabIndex - 1);
    handleTabChange(tabs[prevIndex]);
  }, [handleTabChange, activeTabIndex, tabs]);

  useEffect(() => {
    shouldRedirect && handleTabChange(activeRoute);
  }, [shouldRedirect, handleTabChange, activeRoute]);

  useMemo(() => {
    window.scrollTo(0, 0);
    // eslint-disable-next-line
  }, [location.pathname]);

  return {
    tabs: routes,
    activeTabIndex,
    hasTabs: tabs.length > 1,
    onTabChange: handleTabChange,
    onNextTab: handleNextTab,
    onPrevTab: handlePrevTab,
  };
};

const routes = Object.values(routeConfig);

export default routes;
