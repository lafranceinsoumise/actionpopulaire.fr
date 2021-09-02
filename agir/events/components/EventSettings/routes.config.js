import { lazy } from "@agir/front/app/utils";
import {
  RouteConfig,
  routeConfig as globalRouteConfig,
} from "@agir/front/app/routes.config";

import illustrationManage from "@agir/front/genericComponents/images/group_members.svg";
import illustrationGeneral from "@agir/front/genericComponents/images/group_general.svg";
import illustrationVisio from "@agir/front/genericComponents/images/video-conference.svg";

const EventGeneral = lazy(() =>
  import("@agir/events/EventSettings/EventGeneral")
);
const EventParticipants = lazy(() =>
  import("@agir/events/EventSettings/EventParticipants")
);
const EventOrganization = lazy(() =>
  import("@agir/events/EventSettings/EventOrganization")
);
const EventVisio = lazy(() => import("@agir/events/EventSettings/EventVisio"));
const EventContact = lazy(() =>
  import("@agir/events/EventSettings/EventContact")
);
const EventLocation = lazy(() =>
  import("@agir/events/EventSettings/EventLocation")
);
const EventFeedback = lazy(() =>
  import("@agir/events/EventSettings/EventFeedback")
);
const EventCancelation = lazy(() =>
  import("@agir/events/EventSettings/EventCancelation")
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
    illustration: illustrationGeneral,
    Component: EventGeneral,
    isActive: true,
    menuGroup: 1,
  },
  participants: {
    id: "participants",
    path: "participants/",
    exact: true,
    label: "Participant·es",
    icon: "users",
    Component: EventParticipants,
    isActive: true,
    menuGroup: 1,
  },
  organisation: {
    id: "organisation",
    path: "organisation/",
    exact: true,
    label: "Organisation",
    icon: "settings",
    illustration: illustrationManage,
    Component: EventOrganization,
    isActive: true,
    menuGroup: 1,
  },
  videoConference: {
    id: "videoConference",
    path: "video-conference/",
    exact: true,
    label: "Vidéo-conférence",
    icon: "video",
    illustration: illustrationVisio,
    Component: EventVisio,
    isActive: true,
    menuGroup: 2,
  },
  contact: {
    id: "contact",
    path: "contact/",
    exact: true,
    label: "Contact",
    icon: "mail",
    Component: EventContact,
    isActive: true,
    menuGroup: 2,
  },
  localisation: {
    id: "localisation",
    path: "localisation/",
    exact: true,
    label: "Localisation",
    icon: "map-pin",
    Component: EventLocation,
    isActive: true,
    menuGroup: 2,
  },
  feedback: {
    id: "feedback",
    path: "compte-rendu/",
    exact: true,
    label: "Compte-rendu",
    icon: "image",
    Component: EventFeedback,
    isActive: true,
    canDisabled: true,
    textDisabled: "A remplir à la fin de l'événement",
    menuGroup: 2,
  },
  cancelation: {
    id: "cancelation",
    path: "annuler/",
    exact: true,
    label: "Annuler l'événement",
    icon: "",
    Component: EventCancelation,
    isActive: true,
    menuGroup: 3,
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
