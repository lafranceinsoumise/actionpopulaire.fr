import pathToRegexp from "path-to-regexp-es";

import style from "@agir/front/genericComponents/_variables.scss";
import logger from "@agir/lib/utils/logger";
import { lazy } from "./utils";

import { AUTHENTICATION } from "@agir/front/authentication/common";

const AgendaPage = lazy(() => import("@agir/events/agendaPage/AgendaPage"));
const EventMap = lazy(() => import("@agir/carte/page__eventMap/EventMap"));
const EventPage = lazy(() => import("@agir/events/eventPage/EventPage"));
const CreateEvent = lazy(() =>
  import("@agir/events/createEventPage/CreateEvent")
);
const EventSettings = lazy(() => import("@agir/events/EventSettings"));

const GroupsPage = lazy(() => import("@agir/groups/groupsPage/GroupsPage"));
const FullGroupPage = lazy(() =>
  import("@agir/groups/fullGroupPage/FullGroupPage")
);
const GroupPage = lazy(() => import("@agir/groups/groupPage/GroupPage"));
const GroupSettings = lazy(() =>
  import("@agir/groups/groupPage/GroupSettings")
);
const GroupSettingsMembers = lazy(() =>
  import("@agir/groups/groupPage/GroupSettings/Menus/MenuMembers")
);
const GroupSettingsManage = lazy(() =>
  import("@agir/groups/groupPage/GroupSettings/Menus/MenuManagement")
);
const GroupSettingsFinance = lazy(() =>
  import("@agir/groups/groupPage/GroupSettings/Menus/MenuFinance")
);
const GroupSettingsGeneral = lazy(() =>
  import("@agir/groups/groupPage/GroupSettings/Menus/MenuGeneral")
);
const GroupSettingsLocation = lazy(() =>
  import("@agir/groups/groupPage/GroupSettings/Menus/MenuLocation")
);
const GroupSettingsContact = lazy(() =>
  import("@agir/groups/groupPage/GroupSettings/Menus/MenuContact")
);
const GroupSettingsLinks = lazy(() =>
  import("@agir/groups/groupPage/GroupSettings/Menus/MenuLinks")
);

const GroupMessagePage = lazy(() =>
  import("@agir/groups/groupPage/GroupMessagePage")
);
const GroupMap = lazy(() => import("@agir/carte/page__groupMap/GroupMap"));

const ActivityPage = lazy(() =>
  import("@agir/activity/page__activities/ActivityPage")
);
const RequiredActivityPage = lazy(() =>
  import("@agir/activity/page__requiredActivities/RequiredActivityPage")
);

const NavigationPage = lazy(() =>
  import("@agir/front/navigationPage/NavigationPage")
);

const SignupPage = lazy(() =>
  import("@agir/front/authentication/Connexion/SignupPage")
);
const LoginPage = lazy(() =>
  import("@agir/front/authentication/Connexion/LoginPage")
);
const CodeLoginPage = lazy(() =>
  import("@agir/front/authentication/Connexion/Code/CodeLogin")
);
const CodeSignupPage = lazy(() =>
  import("@agir/front/authentication/Connexion/Code/CodeSignup")
);
const TellMorePage = lazy(() =>
  import("@agir/front/authentication/Connexion/TellMore/TellMorePage")
);
const LogoutPage = lazy(() =>
  import("@agir/front/authentication/Connexion/Logout")
);

export const BASE_PATH = "/";

const log = logger(__filename);

export class RouteConfig {
  constructor(props) {
    Object.keys(props).forEach((key) => (this[key] = props[key]));

    this.__keys__ = [];
    const path = Array.isArray(this.path) ? this.path[0] : this.path;
    this.__re__ = pathToRegexp(this.path, this.__keys__);
    this.__toPath__ = pathToRegexp.compile(path);

    this.match = this.match.bind(this);
    this.getLink = this.getLink.bind(this);
  }

  /**
   * Method to match a pathname string against the RouteConfig path
   * @param  {string} pathname The pathname to match against the RouteConfig path
   * @return {boolean} True if the argument path matches, false otherwise
   */
  match(pathname) {
    return !!pathname && !!this.__re__.exec(pathname);
  }

  /**
   * Method to build a link to the RouteConfig pathname with optional URL parameters
   * @param  {object} params An object mapping the path parameters value
   * @return {string} The link path string
   */
  getLink(params) {
    try {
      params = {
        ...(this.params || {}),
        ...(params || {}),
      };
      return this.__toPath__(params);
    } catch (e) {
      log.error("Failed to generate path", e);
      return Array.isArray(this.path) ? this.path[0] : this.path;
    }
  }
}

const notificationSettingRoute = new RouteConfig({
  id: "notificationSettings",
  path: "/:root/parametres/",
  exact: true,
  neededAuthentication: AUTHENTICATION.HARD,
  label: "Paramètres de notification",
  params: { root: "activite" },
  hideTopBar: true,
  hideFeedbackButton: true,
  hideConnectivityWarning: true,
  hasLayout: false,
  isPartial: true,
});

export const routeConfig = {
  events: new RouteConfig({
    id: "events",
    path: "/",
    exact: true,
    neededAuthentication: AUTHENTICATION.NONE,
    label: "Événements",
    Component: AgendaPage,
    hasLayout: false,
    hideFeedbackButton: true,
    hideTopBar: true,
    hideConnectivityWarning: true,
  }),
  eventMap: new RouteConfig({
    id: "eventMap",
    path: "/evenements/carte/",
    exact: true,
    neededAuthentication: AUTHENTICATION.NONE,
    label: "Carte des événements",
    Component: EventMap,
  }),
  createEvent: new RouteConfig({
    id: "createEvent",
    path: "/evenements/creer/",
    exact: false,
    neededAuthentication: AUTHENTICATION.SOFT,
    label: "Nouvel événement",
    Component: CreateEvent,
    backLink: {
      route: "events",
      label: "Liste des événements",
      isProtected: true,
    },
  }),
  eventDetails: new RouteConfig({
    id: "eventDetails",
    path: "/evenements/:eventPk/",
    exact: true,
    neededAuthentication: AUTHENTICATION.NONE,
    label: "Details de l'événement",
    Component: EventPage,
    backLink: {
      route: "events",
      label: "Liste des événements",
      isProtected: true,
    },
  }),
  eventSettings: new RouteConfig({
    id: "eventSettings",
    path: "/evenements/:eventPk/parametres/",
    exact: true,
    neededAuthentication: AUTHENTICATION.NONE,
    label: "Paramètres de l'événement",
    Component: EventSettings,
    hideTopBar: true,
    hideFeedbackButton: true,
  }),
  groups: new RouteConfig({
    id: "groups",
    path: "/mes-groupes/",
    exact: true,
    neededAuthentication: AUTHENTICATION.SOFT,
    label: "Groupes",
    Component: GroupsPage,
    hasLayout: true,
    layoutProps: {
      smallBackgroundColor: style.black25,
    },
  }),
  groupMap: new RouteConfig({
    id: "groupMap",
    path: "/groupes/carte/",
    exact: true,
    neededAuthentication: AUTHENTICATION.NONE,
    label: "Carte des groupes",
    Component: GroupMap,
  }),
  fullGroup: new RouteConfig({
    id: "fullGroup",
    path: "/groupes/:groupPk/complet/",
    exact: true,
    neededAuthentication: AUTHENTICATION.NONE,
    label: "Groupe complet",
    Component: FullGroupPage,
    hasLayout: false,
  }),
  groupSettings: new RouteConfig({
    id: "groupSettings",
    path: "/groupes/:groupPk/parametres/",
    exact: true,
    neededAuthentication: AUTHENTICATION.NONE,
    label: "Paramètres du groupe",
    Component: GroupSettings,
    hideTopBar: true,
    hideFeedbackButton: true,
  }),
  groupSettingsMembers: new RouteConfig({
    id: "groupSettingsMembers",
    path: "/groupes/:groupPk/parametres/membres/",
    exact: true,
    neededAuthentication: AUTHENTICATION.NONE,
    label: "Membres",
    Component: GroupSettingsMembers,
    hideTopBar: true,
    hideFeedbackButton: true,
  }),
  groupSettingsManage: new RouteConfig({
    id: "groupSettingsManage",
    path: "/groupes/:groupPk/parametres/gestion/",
    exact: true,
    neededAuthentication: AUTHENTICATION.NONE,
    label: "Gestion",
    Component: GroupSettingsManage,
    hideTopBar: true,
    hideFeedbackButton: true,
  }),
  groupSettingsFinance: new RouteConfig({
    id: "groupSettingsFinance",
    path: "/groupes/:groupPk/parametres/finance/",
    exact: true,
    neededAuthentication: AUTHENTICATION.NONE,
    label: "Financement",
    Component: GroupSettingsFinance,
    hideTopBar: true,
    hideFeedbackButton: true,
  }),
  groupSettingsGeneral: new RouteConfig({
    id: "groupSettingsGeneral",
    path: "/groupes/:groupPk/parametres/general/",
    exact: true,
    neededAuthentication: AUTHENTICATION.NONE,
    label: "Général",
    Component: GroupSettingsGeneral,
    hideTopBar: true,
    hideFeedbackButton: true,
  }),
  groupSettingsLocation: new RouteConfig({
    id: "groupSettingsLocation",
    path: "/groupes/:groupPk/parametres/localisation/",
    exact: true,
    neededAuthentication: AUTHENTICATION.NONE,
    label: "Localisation",
    Component: GroupSettingsLocation,
    hideTopBar: true,
    hideFeedbackButton: true,
  }),
  groupSettingsContact: new RouteConfig({
    id: "groupSettingsContact",
    path: "/groupes/:groupPk/parametres/contact/",
    exact: true,
    neededAuthentication: AUTHENTICATION.NONE,
    label: "Contact",
    Component: GroupSettingsContact,
    hideTopBar: true,
    hideFeedbackButton: true,
  }),
  groupSettingsLinks: new RouteConfig({
    id: "groupSettingsLinks",
    path: "/groupes/:groupPk/parametres/liens/",
    exact: true,
    neededAuthentication: AUTHENTICATION.NONE,
    label: "Liens",
    Component: GroupSettingsLinks,
    hideTopBar: true,
    hideFeedbackButton: true,
  }),
  groupMessage: new RouteConfig({
    id: "groupMessage",
    path: "/groupes/:groupPk/messages/:messagePk/",
    exact: true,
    neededAuthentication: AUTHENTICATION.SOFT,
    label: "Message du groupe",
    Component: GroupMessagePage,
    hideFeedbackButton: true,
  }),
  groupDetails: new RouteConfig({
    id: "groupDetails",
    path: "/groupes/:groupPk/:activeTab?/",
    exact: true,
    neededAuthentication: AUTHENTICATION.NONE,
    label: "Details du groupe",
    Component: GroupPage,
    backLink: {
      route: "groups",
      label: "Retour à l'accueil",
      isProtected: true,
    },
  }),
  activities: new RouteConfig({
    id: "activities",
    path: ["/activite/", "/activite/parametres/"],
    exact: true,
    neededAuthentication: AUTHENTICATION.SOFT,
    label: "Actualités",
    Component: ActivityPage,
    hasLayout: true,
    layoutProps: {
      smallBackgroundColor: style.black25,
    },
    topBarRightLink: {
      label: notificationSettingRoute.label,
      to: notificationSettingRoute.getLink({ root: "activite" }),
      protected: true,
    },
  }),
  requiredActivities: new RouteConfig({
    id: "requiredActivities",
    path: ["/a-traiter/", "/a-traiter/parametres/"],
    exact: true,
    neededAuthentication: AUTHENTICATION.SOFT,
    label: "À traiter",
    Component: RequiredActivityPage,
    hasLayout: true,
    topBarRightLink: {
      label: notificationSettingRoute.label,
      to: notificationSettingRoute.getLink({ root: "a-traiter" }),
      protected: true,
    },
  }),
  notificationSettings: notificationSettingRoute,
  menu: new RouteConfig({
    id: "menu",
    path: "/navigation/",
    exact: true,
    neededAuthentication: AUTHENTICATION.SOFT,
    label: "Menu",
    Component: NavigationPage,
    hasLayout: true,
    layoutProps: {
      desktopOnlyFooter: false,
      displayFooterOnMobileApp: true,
      style: { paddingBottom: 0 },
    },
  }),
  login: new RouteConfig({
    id: "login",
    path: "/connexion/",
    exact: true,
    neededAuthentication: AUTHENTICATION.NONE,
    label: "Connexion",
    Component: LoginPage,
    hideTopBar: true,
    hideFeedbackButton: true,
  }),
  signup: new RouteConfig({
    id: "signup",
    path: "/inscription/",
    exact: true,
    neededAuthentication: AUTHENTICATION.NONE,
    label: "Inscription",
    Component: SignupPage,
    hideTopBar: true,
    hideFeedbackButton: true,
  }),
  codeLogin: new RouteConfig({
    id: "codeLogin",
    path: "/connexion/code/",
    exact: true,
    neededAuthentication: AUTHENTICATION.NONE,
    label: "Code de connexion",
    Component: CodeLoginPage,
    hideTopBar: true,
    hideFeedbackButton: true,
  }),
  codeSignup: new RouteConfig({
    id: "codeSignup",
    path: "/inscription/code/",
    exact: true,
    neededAuthentication: AUTHENTICATION.NONE,
    label: "Code d'inscription'",
    Component: CodeSignupPage,
    hideTopBar: true,
    hideFeedbackButton: true,
  }),
  tellMore: new RouteConfig({
    id: "tellMore",
    path: "/bienvenue/",
    exact: true,
    neededAuthentication: AUTHENTICATION.NONE,
    label: "J'en dis plus",
    Component: TellMorePage,
    hideTopBar: true,
    hideFeedbackButton: true,
    hidePushModal: true,
  }),
  logout: new RouteConfig({
    id: "logout",
    path: "/deconnexion/",
    exact: true,
    neededAuthentication: AUTHENTICATION.NONE,
    label: "Déconnexion",
    Component: LogoutPage,
  }),
};

export const getRouteByPathname = (pathname) => {
  return Object.values(routeConfig).find(
    (route) => route.path === pathname || route.match(pathname)
  );
};

const routes = Object.values(routeConfig).filter((route) => !route.isPartial);

export default routes;
