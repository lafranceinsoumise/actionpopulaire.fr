import { lazy } from "@agir/front/app/utils";
import {
  RouteConfig,
  routeConfig as globalRouteConfig,
} from "@agir/front/app/routes.config";

import illustrationManage from "@agir/front/genericComponents/images/group_members.svg";
import illustrationGeneral from "@agir/front/genericComponents/images/group_general.svg";
import illustrationVisio from "@agir/front/genericComponents/images/video-conference.svg";

const EventSettingsGeneral = lazy(
  () =>
    import(
      /* webpackChunkName: "r-eventsettingsgeneral" */ "@agir/events/EventSettings/EventGeneral"
    ),
);
const EventSettingsParticipants = lazy(
  () =>
    import(
      /* webpackChunkName: "r-eventsettingsparticipants" */ "@agir/events/EventSettings/EventParticipants"
    ),
);
const EventSettingsOrganization = lazy(
  () =>
    import(
      /* webpackChunkName: "r-eventsettingsorganization" */ "@agir/events/EventSettings/EventOrganization"
    ),
);
const EventSettingsVisio = lazy(
  () =>
    import(
      /* webpackChunkName: "r-eventsettingsvisio" */ "@agir/events/EventSettings/EventVisio"
    ),
);
const EventSettingsContact = lazy(
  () =>
    import(
      /* webpackChunkName: "r-eventsettingscontact" */ "@agir/events/EventSettings/EventContact"
    ),
);
const EventSettingsLocation = lazy(
  () =>
    import(
      /* webpackChunkName: "r-eventsettingslocation" */ "@agir/events/EventSettings/EventLocation"
    ),
);
const EventSettingsFeedback = lazy(
  () =>
    import(
      /* webpackChunkName: "r-eventsettingsfeedback" */ "@agir/events/EventSettings/EventFeedback"
    ),
);
const EventSettingsCancelation = lazy(
  () =>
    import(
      /* webpackChunkName: "r-eventsettingscancelation" */ "@agir/events/EventSettings/EventCancelation"
    ),
);
const EventSettingsDocuments = lazy(
  () =>
    import(
      /* webpackChunkName: "r-eventsettingsdocuments" */ "@agir/events/EventSettings/EventDocuments"
    ),
);
const EventSettingsAssets = lazy(
  () =>
    import(
      /* webpackChunkName: "r-eventsettingsassets" */ "@agir/events/EventSettings/EventAssets"
    ),
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
    Component: EventSettingsGeneral,
    isActive: true,
    menuGroup: 1,
  },
  participants: {
    id: "participants",
    path: "participants/",
    exact: true,
    label: "Participant·es",
    icon: "users",
    Component: EventSettingsParticipants,
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
    Component: EventSettingsOrganization,
    isActive: true,
    menuGroup: 1,
  },
  documents: {
    id: "documents",
    path: "documents/",
    exact: true,
    label: "Documents",
    icon: "file-text",
    Component: EventSettingsDocuments,
    isActive: (event) => event.hasProject,
    menuGroup: 1,
  },
  videoConference: {
    id: "videoConference",
    path: "video-conference/",
    exact: true,
    label: "Vidéo-conférence",
    icon: "video",
    illustration: illustrationVisio,
    Component: EventSettingsVisio,
    isActive: true,
    menuGroup: 2,
  },
  contact: {
    id: "contact",
    path: "contact/",
    exact: true,
    label: "Contact",
    icon: "mail",
    Component: EventSettingsContact,
    isActive: true,
    menuGroup: 2,
  },
  localisation: {
    id: "localisation",
    path: "localisation/",
    exact: true,
    label: "Localisation",
    icon: "map-pin",
    Component: EventSettingsLocation,
    isActive: true,
    menuGroup: 2,
  },
  feedback: {
    id: "feedback",
    path: "compte-rendu/",
    exact: true,
    label: "Compte rendu",
    icon: "image",
    Component: EventSettingsFeedback,
    isActive: true,
    menuGroup: 2,
  },
  assets: {
    id: "assets",
    path: "ressources/",
    exact: true,
    label: "Ressources",
    icon: "more-horizontal",
    Component: EventSettingsAssets,
    isActive: true,
    menuGroup: 2,
  },
  cancelation: {
    id: "cancelation",
    path: "annuler/",
    exact: true,
    label: "Annuler l'événement",
    icon: "",
    Component: EventSettingsCancelation,
    isActive: (event) => event.isEditable && !event.isPast,
    menuGroup: 3,
    isCancel: true,
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
        disabled:
          typeof route?.disabled === "function"
            ? route.disabled(event)
            : route.disabled === true,
        path: basePath + menuRoute.path + route.path,
      }),
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
