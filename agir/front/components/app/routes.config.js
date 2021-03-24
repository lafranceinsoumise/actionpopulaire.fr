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

const GroupsPage = lazy(() => import("@agir/groups/groupsPage/GroupsPage"));
const FullGroupPage = lazy(() =>
  import("@agir/groups/fullGroupPage/FullGroupPage")
);
const GroupPage = lazy(() => import("@agir/groups/groupPage/GroupPage"));
const GroupMessagePage = lazy(() =>
  import("@agir/groups/groupPage/GroupMessagePage")
);
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

const IntroAppPage = lazy(() => import("@agir/front/app/IntroApp"));
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
const ChooseCampaignPage = lazy(() =>
  import("@agir/front/authentication/Connexion/TellMore/ChooseCampaign")
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
    const pathname = Array.isArray(this.pathname)
      ? this.pathname[0]
      : this.pathname;
    this.__re__ = pathToRegexp(this.pathname, this.__keys__);
    this.__toPath__ = pathToRegexp.compile(pathname);

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
      params = {
        ...(this.params || {}),
        ...(params || {}),
      };
      return this.__toPath__(params);
    } catch (e) {
      log.error("Failed to generate path", e);
      return Array.isArray(this.pathname) ? this.pathname[0] : this.pathname;
    }
  }
}

export const routeConfig = {
  events: new RouteConfig({
    id: "events",
    pathname: "/",
    exact: true,
    neededAuthentication: AUTHENTICATION.NONE,
    label: "Événements",
    Component: AgendaPage,
    hasLayout: false,
  }),
  eventMap: new RouteConfig({
    id: "eventMap",
    pathname: "/evenements/carte/",
    exact: true,
    neededAuthentication: AUTHENTICATION.SOFT,
    label: "Carte des événements",
    Component: EventMap,
  }),
  createEvent: new RouteConfig({
    id: "createEvent",
    pathname: "/evenements/creer/",
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
    pathname: "/evenements/:eventPk/",
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
  groups: new RouteConfig({
    id: "groups",
    pathname: "/mes-groupes/",
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
    pathname: "/groupes/carte/",
    exact: true,
    neededAuthentication: AUTHENTICATION.SOFT,
    label: "Carte des groupes",
    Component: GroupMap,
  }),
  fullGroup: new RouteConfig({
    id: "fullGroup",
    pathname: "/groupes/:groupPk/complet/",
    exact: true,
    neededAuthentication: AUTHENTICATION.NONE,
    label: "Groupe complet",
    Component: FullGroupPage,
    hasLayout: false,
  }),
  groupMessage: new RouteConfig({
    id: "groupMessage",
    pathname: "/groupes/:groupPk/messages/:messagePk/",
    exact: true,
    neededAuthentication: AUTHENTICATION.SOFT,
    label: "Message du groupe",
    Component: GroupMessagePage,
    hideFeedbackButton: true,
  }),
  groupDetails: new RouteConfig({
    id: "groupDetails",
    pathname: "/groupes/:groupPk/:activeTab?/",
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
    pathname: "/activite/",
    exact: true,
    neededAuthentication: AUTHENTICATION.SOFT,
    label: "Actualités",
    Component: ActivityPage,
    hasLayout: true,
    layoutProps: {
      smallBackgroundColor: style.black25,
      title: "Actualités",
      subtitle: "L'actualité de vos groupes et de votre engagement",
    },
  }),
  requiredActivities: new RouteConfig({
    id: "requiredActivities",
    pathname: "/a-traiter/",
    exact: true,
    neededAuthentication: AUTHENTICATION.SOFT,
    label: "À traiter",
    Component: RequiredActivityPage,
    hasLayout: true,
  }),
  menu: new RouteConfig({
    id: "menu",
    pathname: "/navigation/",
    exact: true,
    neededAuthentication: AUTHENTICATION.SOFT,
    label: "Menu",
    Component: NavigationPage,
    hasLayout: true,
    layoutProps: {
      desktopOnlyFooter: false,
    },
  }),
  login: new RouteConfig({
    id: "login",
    pathname: "/connexion/",
    exact: true,
    neededAuthentication: AUTHENTICATION.NONE,
    label: "Connexion",
    Component: LoginPage,
  }),
  signup: new RouteConfig({
    id: "signup",
    pathname: "/inscription/",
    exact: true,
    neededAuthentication: AUTHENTICATION.NONE,
    label: "Inscription",
    Component: SignupPage,
  }),
  codeLogin: new RouteConfig({
    id: "codeLogin",
    pathname: "/connexion/code/",
    exact: true,
    neededAuthentication: AUTHENTICATION.NONE,
    label: "Code de connexion",
    Component: CodeLoginPage,
  }),
  codeSignup: new RouteConfig({
    id: "codeSignup",
    pathname: "/inscription/code/",
    exact: true,
    neededAuthentication: AUTHENTICATION.NONE,
    label: "Code d'inscription'",
    Component: CodeSignupPage,
  }),
  tellMore: new RouteConfig({
    id: "tellMore",
    pathname: "/bienvenue/",
    exact: true,
    neededAuthentication: AUTHENTICATION.NONE,
    label: "J'en dis plus",
    Component: TellMorePage,
  }),
  introApp: new RouteConfig({
    id: "introApp",
    pathname: "/intro/",
    exact: true,
    neededAuthentication: AUTHENTICATION.NONE,
    label: "Intro",
    Component: IntroAppPage,
    hasLayout: false,
    layoutProps: {
      smallBackgroundColor: style.black25,
      hasBanner: false,
    },
  }),
  logout: new RouteConfig({
    id: "logout",
    pathname: "/deconnexion/",
    exact: true,
    neededAuthentication: AUTHENTICATION.NONE,
    label: "Déconnexion",
    Component: LogoutPage,
  }),
};

const routes = Object.values(routeConfig).filter(Boolean);

export const getRouteByPathname = (pathname) => {
  return routes.find(
    (route) => route.pathname === pathname || route.match(pathname)
  );
};

export default routes;
