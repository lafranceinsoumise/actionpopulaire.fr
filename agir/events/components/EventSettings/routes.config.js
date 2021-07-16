import { lazy } from "@agir/front/app/utils";
import {
  RouteConfig,
  routeConfig as globalRouteConfig,
} from "@agir/front/app/routes.config";

// import illustrationManage from "@agir/front/genericComponents/images/group_members.svg";

const EventGeneral = lazy(() =>
  import("@agir/events/EventSettings/EventGeneral")
);


export const menuRoute = {
  id: "menu",
  path: "gestion/",
  exact: false,
  label: "Paramètres de l'événement",
};

export const routeConfig = {
  general: {
    id: "general",
    path: "general/",
    exact: true,
    label: "Général",
    icon: "file",
    Component: EventGeneral,
    isActive: true,
    menuGroup: 1,
  },
  members: {
    id: "members",
    path: "membres/",
    exact: true,
    label: "X participant.es",
    icon: "users",
    Component: EventGeneral,
    isActive: true,
    menuGroup: 1,
  },
  organisation: {
    id: "organisation",
    path: "organisation/",
    exact: true,
    label: "Co-organisation",
    icon: "settings",
    Component: EventGeneral,
    isActive: true,
    menuGroup: 1,
  },
  rights: {
    id: "rights",
    path: "droits/",
    exact: true,
    label: "Droits",
    icon: "lock",
    Component: EventGeneral,
    isActive: true,
    menuGroup: 1,
  },
  videoConference: {
    id: "videoConference",
    path: "video-conference/",
    exact: true,
    label: "Vidéo-conférence",
    icon: "video",
    Component: EventGeneral,
    isActive: true,
    menuGroup: 2,
  },
  contact: {
    id: "contact",
    path: "contact/",
    exact: true,
    label: "Contact",
    icon: "mail",
    Component: EventGeneral,
    isActive: true,
    menuGroup: 2,
  },
  localisation: {
    id: "localisation",
    path: "localisation/",
    exact: true,
    label: "Localisation",
    icon: "map-pin",
    Component: EventGeneral,
    isActive: true,
    menuGroup: 2,
  },
};

export const getMenuRoute = (basePath) =>
  new RouteConfig({
    ...menuRoute,
    path: basePath + menuRoute.path,
  });

const getActiveRoutes = (event) =>
  Object.values(routeConfig).filter((route) => {
    if (typeof route.isActive === "function") {
      return !!route.isActive(event);
    }
    return !!route.isActive;
  });

export const getRoutes = (basePath, event) =>
  getActiveRoutes(event).map(
    (route) =>
      new RouteConfig({
        ...route,
        path: basePath + menuRoute.path + route.path,
      })
  );

export const getEventSettingLinks = (event, basePath) => {
  const links = {};

  if (!event?.id || !event.isManager) {
    return links;
  }

  if (!basePath) {
    const activeRoutes = getActiveRoutes(event);
    links.menu = globalRouteConfig.eventSettings.getLink({
      eventPk: event.id,
    });
    activeRoutes.forEach((route) => {
      links[route.id] = globalRouteConfig.eventSettings.getLink({
        activePanel: route.path.replace("/", "") || null,
        eventPk: event.id,
      });
    });
    return links;
  }

  const activeRoutes = getRoutes(basePath, event);
  links.menu = getMenuRoute(basePath).getLink();
  activeRoutes.forEach((route) => {
    links[route.id] = route.getLink();
  });

  return links;
};

export default getRoutes;
