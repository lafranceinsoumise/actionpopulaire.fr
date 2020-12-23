import pathToRegexp from "path-to-regexp-es";
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

class RouteConfig {
  constructor(props) {
    Object.keys(props).forEach((key) => (this[key] = props[key]));

    this.__keys__ = [];
    this.__re__ = pathToRegexp(this.pathname, this.__keys__);
    this.__toPath__ = pathToRegexp.compile(this.pathname);

    this.match = this.match.bind(this);
    this.getLink = this.getLink.bind(this);
  }

  /**
   * Method to match a path string against the RouteConfig pathname
   * @param  {string} path The path to match against the RouteConfig pathname
   * @return {boolean} True if the argument path matches, false otherwise
   */
  match(path) {
    return !!path && !!this.__re__.exec(path);
  }

  /**
   * Method to build a link to the RouteConfig pathname with optional URL parameters
   * @param  {object} params An object mapping the path parameters value
   * @return {string} The link path string
   */
  getLink(params) {
    try {
      params = params || {};
      return this.__toPath__(params);
    } catch (e) {
      return this.pathname;
    }
  }
}

export const routeConfig = {
  events: new RouteConfig({
    id: "events",
    pathname: "/",
    exact: true,
    label: "Événements",
    Component: AgendaPage,
  }),
  eventMap: new RouteConfig({
    id: "eventMap",
    pathname: "/evenements/carte",
    exact: true,
    label: "Carte des événements",
    Component: EventMap,
  }),
  eventDetails: new RouteConfig({
    id: "eventDetails",
    pathname: "/evenements/:eventPk",
    exact: true,
    label: "Details de l'événement",
    Component: EventPage,
  }),
  groups: new RouteConfig({
    id: "groups",
    pathname: "/mes-groupes/",
    exact: true,
    label: "Groupes",
    Component: GroupsPage,
  }),
  groupMap: new RouteConfig({
    id: "groupMap",
    pathname: "/groupes/carte",
    exact: true,
    label: "Carte des groupes",
    Component: GroupMap,
  }),
  activities: new RouteConfig({
    id: "activities",
    pathname: "/activite/",
    exact: true,
    label: "Actualités",
    Component: ActivityPage,
  }),
  requiredActivities: new RouteConfig({
    id: "requiredActivities",
    pathname: "/a-traiter/",
    exact: true,
    label: "À traiter",
    Component: RequiredActivityPage,
  }),
  menu: new RouteConfig({
    id: "menu",
    pathname: "/navigation/",
    exact: true,
    label: "Menu",
    Component: NavigationPage,
  }),
};

const routes = Object.values(routeConfig).filter(Boolean);

export const getRouteByPathname = (pathname) => {
  return routes.find(
    (route) => route.pathname === pathname || route.match(pathname)
  );
};

export default routes;
