import { lazy } from "react";

const AgendaPage = lazy(() => import("@agir/events/agendaPage/AgendaPage"));
const EventMap = lazy(() => import("@agir/carte/page__eventMap/EventMap"));
const EventPage = lazy(() => import("@agir/events/eventPage/EventPage"));

const GroupsPage = lazy(() => import("@agir/groups/groupsPage/GroupsPage"));
const GroupMap = lazy(() => import("@agir/carte/page__groupMap/GroupMap"));

const ActivityPage = lazy(() =>
  import("@agir/activity/page__activities/ActivityPage")
);
const RequiredActivityPage = lazy(() =>
  import("@agir/activity/page__requiredActivities/RequiredActivityList")
);
const NavigationPage = lazy(() =>
  import("@agir/front/navigationPage/NavigationPage")
);

export const BASE_PATH = "/";

export const routeConfig = {
  events: {
    id: "events",
    pathname: "/",
    exact: true,
    label: "Événements",
    Component: AgendaPage,
  },
  eventMap: {
    id: "eventMap",
    pathname: "/evenements/carte",
    exact: true,
    label: "Carte des événements",
    Component: EventMap,
  },
  eventDetails: {
    id: "eventDetails",
    pathname: "/evenements/:eventPk",
    exact: true,
    label: "Details de l'événement",
    Component: EventPage,
  },
  groups: {
    id: "groups",
    pathname: "/mes-groupes/",
    exact: true,
    label: "Groupes",
    Component: GroupsPage,
  },
  groupMap: {
    id: "groupMap",
    pathname: "/groupes/carte",
    exact: true,
    label: "Carte des groupes",
    Component: GroupMap,
  },
  activities: {
    id: "activities",
    pathname: "/activite/",
    exact: true,
    label: "Actualités",
    Component: ActivityPage,
  },
  requiredActivities: {
    id: "requiredActivities",
    pathname: "/a-traiter/",
    exact: true,
    label: "À traiter",
    Component: RequiredActivityPage,
  },
  menu: {
    id: "menu",
    pathname: "/navigation/",
    exact: true,
    label: "Menu",
    Component: NavigationPage,
  },
};

const routes = Object.values(routeConfig);

export const getRouteByPathname = (pathname) => {
  return routes.find((route) => route.pathname === pathname);
};

export default routes;
