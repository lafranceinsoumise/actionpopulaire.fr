import { useCallback, useEffect, useMemo } from "react";
import { useHistory, useLocation } from "react-router-dom";
import { RouteConfig } from "@agir/front/app/routes.config";

import { useDispatch } from "@agir/front/globalContext/GlobalContext";
import {
  setTopBarRightLink,
  setAdminLink,
} from "@agir/front/globalContext/actions";

import { getMenuRoute as getSettingsRoute } from "@agir/groups/groupPage/GroupSettings/routes.config";

const routeConfig = {
  info: {
    id: "info",
    path: "/groupes/:groupPk/",
    exact: false,
    label: "Accueil",
    hasTab: true,
    hasRoute: true,
  },
  messages: {
    id: "messages",
    path: "/groupes/:groupPk/messages/",
    exact: false,
    label: "Messages",
    hasTab: true,
    hasRoute: (group) => {
      if (group.isManager) {
        return true;
      }
      return group.isMember && group.hasMessages;
    },
  },
  agenda: {
    id: "agenda",
    path: "/groupes/:groupPk/agenda/",
    exact: false,
    label: "Agenda",
    hasTab: true,
    hasRoute: (group) =>
      group.isMember || group.hasUpcomingEvents || group.hasPastEvents,
  },
  reports: {
    id: "reports",
    path: "/groupes/:groupPk/comptes-rendus/",
    exact: false,
    label: "Comptes rendus",
    hasTab: true,
    hasRoute: (group) => group.isManager || group.hasPastEventReports,
  },
};

export const useTabs = (props, isMobile = true) => {
  const dispatch = useDispatch();
  const history = useHistory();
  const location = useLocation();

  const { group } = props;

  const routes = useMemo(
    () =>
      Object.values(routeConfig)
        .filter((route) =>
          typeof route.hasRoute === "function"
            ? route.hasRoute(group, isMobile)
            : route.hasRoute,
        )
        .map(
          (route) =>
            new RouteConfig({
              ...route,
              params: { groupPk: group.id },
            }),
        ),
    [group, isMobile],
  );

  const tabs = useMemo(() => routes.filter((route) => route.hasTab), [routes]);

  const activeRoute = useMemo(() => {
    let result = tabs[0];
    routes.forEach((route) => {
      if (route.match(location.pathname)) {
        result = route;
      }
    });
    return result;
  }, [tabs, routes, location.pathname]);

  const activePathname = activeRoute.getLink();
  const settingsLink = useMemo(
    () =>
      group?.id && group.isManager
        ? getSettingsRoute(activePathname).getLink()
        : null,
    [group, activePathname],
  );

  const activeTabIndex = useMemo(() => {
    for (let i = 0; tabs[i]; i++) {
      if (activeRoute === tabs[i]) {
        return i;
      }
    }
  }, [tabs, activeRoute]);

  const handleTabChange = useCallback(
    (route, params, shouldReplace) => {
      if (route && route.getLink) {
        shouldReplace
          ? history.replace(route.getLink(params))
          : history.push(route.getLink(params));
      }
    },
    [history],
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
    const { routes } = group || {};
    routes &&
      routes.admin &&
      dispatch(
        setAdminLink({
          href: routes.admin,
          label: "Administration",
        }),
      );
  }, [dispatch, group, activePathname]);

  useEffect(() => {
    settingsLink &&
      dispatch(
        setTopBarRightLink({
          to: settingsLink,
          label: "Gestion du groupe",
        }),
      );
  }, [dispatch, settingsLink, location.pathname]);

  useMemo(() => {
    window.scrollTo(0, 0);
    // eslint-disable-next-line
  }, [activePathname]);

  const result = useMemo(
    () => ({
      tabs: routes,
      activePathname,
      activeTabId: activeRoute.id,
      hasTabs: tabs.length > 1,
      onTabChange: handleTabChange,
      onNextTab: handleNextTab,
      onPrevTab: handlePrevTab,
    }),
    [
      routes,
      activePathname,
      activeRoute.id,
      tabs.length,
      handleTabChange,
      handleNextTab,
      handlePrevTab,
    ],
  );

  return result;
};

const routes = Object.values(routeConfig);

export default routes;
