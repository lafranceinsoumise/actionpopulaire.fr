import pathToRegexp from "path-to-regexp-es";

import style from "@agir/front/genericComponents/_variables.scss";
import logger from "@agir/lib/utils/logger";
import { lazy } from "./utils";

import { AUTHENTICATION } from "@agir/front/authentication/common";

const AgendaPage = lazy(() => import("@agir/events/agendaPage/Agenda"));
const HomePage = lazy(() => import("@agir/front/app/Homepage/Home"));
const EventMap = lazy(() => import("@agir/carte/page__eventMap/EventMap"));
const EventPage = lazy(() => import("@agir/events/eventPage/EventPage"));
const CreateEvent = lazy(() =>
  import("@agir/events/createEventPage/CreateEvent")
);
const MissingDocumentsPage = lazy(() =>
  import(
    "@agir/events/eventRequiredDocuments/MissingDocuments/MissingDocumentsPage"
  )
);
const EventRequiredDocuments = lazy(() =>
  import("@agir/events/eventRequiredDocuments/EventRequiredDocumentsPage")
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
  import("@agir/activity/ActivityPage/ActivityPage")
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
const MessagePage = lazy(() => import("@agir/msgs/MessagePage/MessagePage"));
const CreateContactPage = lazy(() =>
  import("@agir/people/contacts/CreateContactPage")
);
const DonationPage = lazy(() =>
  import("@agir/donations/donationPage/DonationPage")
);
const DonationInformationsPage = lazy(() =>
  import("@agir/donations/donationPage/InformationsPage")
);
const ActionToolsPage = lazy(() =>
  import("@agir/front/ActionToolsPage/ActionToolsPage")
);
const SearchPage = lazy(() => import("@agir/front/SearchPage/SearchPage"));

const NewVotingProxyRequest = lazy(() =>
  import("@agir/voting_proxies/VotingProxyRequest/NewVotingProxyRequest")
);
const NewVotingProxy = lazy(() =>
  import("@agir/voting_proxies/VotingProxy/NewVotingProxy")
);

export const BASE_PATH = "/";

const log = logger(__filename);

export class RouteConfig {
  constructor(props) {
    Object.keys(props).forEach((key) => (this[key] = props[key]));

    this.__keys__ = [];
    const path = Array.isArray(this.path) ? this.path[0] : this.path;
    this.__re__ = pathToRegexp(this.path, this.__keys__, {
      end: this.exact === false ? false : true,
    });
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
  path: "/:root*/parametres/",
  exact: true,
  neededAuthentication: AUTHENTICATION.HARD,
  label: "Paramètres de notification",
  params: { root: "activite" },
  isPartial: true,
});

export const routeConfig = {
  events: new RouteConfig({
    id: "events",
    path: ["/", "/documents-justificatifs/"],
    exact: true,
    neededAuthentication: AUTHENTICATION.SOFT,
    label: "Événements",
    Component: AgendaPage,
    hasLayout: true,
    layoutProps: {
      smallBackgroundColor: style.black25,
    },
    hideFeedbackButton: true,
    keepScroll: true,
    hideFooterBanner: true,
    AnonymousComponent: HomePage,
    anonymousConfig: {
      hasLayout: false,
    },
  }),
  missingEventDocumentsModal: new RouteConfig({
    id: "missingEventDocuments",
    path: "/documents-justificatifs/",
    exact: true,
    neededAuthentication: AUTHENTICATION.SOFT,
    label: "Documents justificatifs",
    hideFeedbackButton: true,
    isPartial: true,
  }),
  missingEventDocuments: new RouteConfig({
    id: "missingEventDocuments",
    path: "/evenements/documents-justificatifs/",
    exact: true,
    neededAuthentication: AUTHENTICATION.HARD,
    label: "Documents justificatifs",
    Component: MissingDocumentsPage,
    hideFeedbackButton: true,
    hasLayout: false,
    backLink: {
      route: "events",
      label: "Liste des événements",
      isProtected: true,
    },
  }),
  eventMap: new RouteConfig({
    id: "eventMap",
    path: "/evenements/carte/",
    exact: true,
    neededAuthentication: AUTHENTICATION.NONE,
    label: "Carte des événements",
    Component: EventMap,
    hideFooter: true,
    hideFeedbackButton: true,
  }),
  createEvent: new RouteConfig({
    id: "createEvent",
    path: "/evenements/creer/",
    exact: false,
    neededAuthentication: AUTHENTICATION.SOFT,
    label: "Nouvel événement",
    hideFeedbackButton: true,
    Component: CreateEvent,
    backLink: {
      route: "events",
      label: "Liste des événements",
      isProtected: true,
    },
    hideFooter: true,
  }),
  eventDetails: new RouteConfig({
    id: "eventDetails",
    path: "/evenements/:eventPk/",
    exact: true,
    neededAuthentication: AUTHENTICATION.NONE,
    label: "Détails de l'événement",
    Component: EventPage,
    backLink: {
      route: "events",
      label: "Liste des événements",
      isProtected: true,
    },
  }),
  eventSettings: new RouteConfig({
    id: "eventSettings",
    path: "/evenements/:eventPk/gestion/:activePanel?/",
    params: { activePanel: null },
    exact: true,
    neededAuthentication: AUTHENTICATION.HARD,
    Component: EventPage,
    hideFeedbackButton: true,
  }),
  eventRequiredDocuments: new RouteConfig({
    id: "eventRequiredDocuments",
    path: "/evenements/:eventPk/documents/",
    exact: true,
    neededAuthentication: AUTHENTICATION.HARD,
    label: "Documents de l'événement",
    Component: EventRequiredDocuments,
    backLink: {
      route: "events",
      label: "Liste des événements",
      isProtected: true,
    },
  }),
  groups: new RouteConfig({
    id: "groups",
    path: "/mes-groupes/",
    exact: true,
    neededAuthentication: AUTHENTICATION.SOFT,
    label: "Mes groupes",
    Component: GroupsPage,
    hasLayout: true,
    layoutProps: {
      smallBackgroundColor: style.black25,
    },
    keepScroll: true,
  }),
  groupMap: new RouteConfig({
    id: "groupMap",
    path: "/groupes/carte/",
    exact: true,
    neededAuthentication: AUTHENTICATION.NONE,
    label: "Carte des groupes",
    Component: GroupMap,
    hideFooter: true,
    hideFeedbackButton: true,
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
    path: "/groupes/:groupPk/:activeTab?/gestion/:activePanel?/",
    params: { activeTab: null, activePanel: null },
    exact: true,
    neededAuthentication: AUTHENTICATION.HARD,
    Component: GroupPage,
    isPartial: true,
  }),
  groupMessage: new RouteConfig({
    id: "groupMessage",
    path: "/groupes/:groupPk/message/:messagePk/",
    exact: true,
    neededAuthentication: AUTHENTICATION.SOFT,
    label: "Message du groupe",
    Component: GroupMessagePage,
    hideFeedbackButton: true,
  }),
  groupDetails: new RouteConfig({
    id: "groupDetails",
    path: "/groupes/:groupPk/:activeTab?/",
    exact: false,
    neededAuthentication: AUTHENTICATION.NONE,
    label: "Détails du groupe",
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
    label: "Notifications",
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
    keepScroll: true,
  }),
  actionTools: new RouteConfig({
    id: "actionTools",
    path: "/agir/",
    exact: true,
    neededAuthentication: AUTHENTICATION.SOFT,
    label: "Agir",
    Component: ActionToolsPage,
    hasLayout: false,
    hideFeedbackButton: true,
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
    displayFooterOnMobileApp: true,
    layoutProps: {
      style: { paddingBottom: 0 },
    },
  }),
  login: new RouteConfig({
    id: "login",
    path: "/connexion/",
    exact: true,
    neededAuthentication: AUTHENTICATION.NONE,
    label: "Connexion",
    description: "Connectez-vous à Action Populaire",
    Component: LoginPage,
    hideTopBar: true,
    hideFeedbackButton: true,
    hideFooter: true,
  }),
  signup: new RouteConfig({
    id: "signup",
    path: "/inscription/",
    exact: true,
    neededAuthentication: AUTHENTICATION.NONE,
    label: "Inscription",
    description: "Rejoignez Action Populaire",
    Component: SignupPage,
    hideTopBar: true,
    hideFeedbackButton: true,
    hideFooter: true,
  }),
  codeLogin: new RouteConfig({
    id: "codeLogin",
    path: "/connexion/code/",
    exact: true,
    neededAuthentication: AUTHENTICATION.NONE,
    label: "Connexion",
    description: "Connectez-vous à Action Populaire",
    Component: CodeLoginPage,
    hideTopBar: true,
    hideFeedbackButton: true,
    hideFooter: true,
  }),
  codeSignup: new RouteConfig({
    id: "codeSignup",
    path: "/inscription/code/",
    exact: true,
    neededAuthentication: AUTHENTICATION.NONE,
    label: "Inscription",
    description: "Rejoignez Action Populaire",
    Component: CodeSignupPage,
    hideTopBar: true,
    hideFeedbackButton: true,
    hideFooter: true,
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
    hideFooter: true,
  }),
  logout: new RouteConfig({
    id: "logout",
    path: "/deconnexion/",
    exact: true,
    neededAuthentication: AUTHENTICATION.NONE,
    label: "Déconnexion",
    Component: LogoutPage,
  }),
  messages: new RouteConfig({
    id: "messages",
    path: ["/messages/:messagePk?/", "/messages/:messagePk/parametres/"],
    params: { messagePk: null },
    exact: true,
    neededAuthentication: AUTHENTICATION.HARD,
    label: "Messages",
    Component: MessagePage,
    hasLayout: false,
    hideFeedbackButton: true,
    hideFooter: true,
  }),
  createContact: new RouteConfig({
    id: "createContact",
    path: "/contacts/creer/:step?/",
    params: { step: null },
    exact: true,
    neededAuthentication: AUTHENTICATION.SOFT,
    label: "Nouveau contact",
    Component: CreateContactPage,
    hasLayout: false,
    hideFeedbackButton: true,
    hideFooter: true,
  }),
  donations: new RouteConfig({
    id: "donations",
    path: "/:type?/dons/",
    params: { type: null },
    exact: true,
    neededAuthentication: AUTHENTICATION.NONE,
    label: "Faire un don",
    Component: DonationPage,
    hasLayout: false,
    hideFeedbackButton: true,
    hideFooter: true,
    appOnlyTopBar: true,
  }),
  donationsInformations: new RouteConfig({
    id: "donationsInformations",
    params: { type: null },
    path: ["/:type?/dons/informations/", "/:type?/dons-mensuels/informations/"],
    exact: true,
    neededAuthentication: AUTHENTICATION.NONE,
    label: "Faire un don",
    Component: DonationInformationsPage,
    hasLayout: false,
    hideFeedbackButton: true,
    hideFooter: true,
    appOnlyTopBar: true,
  }),
  donationsInformationsModal: new RouteConfig({
    id: "donationsInformationsModal",
    params: { type: null },
    path: ["/:type?/dons/informations-modal/"],
    exact: true,
    neededAuthentication: AUTHENTICATION.NONE,
    label: "Faire un don",
    Component: DonationPage,
    hasLayout: false,
    hideFeedbackButton: true,
    hideFooter: true,
    appOnlyTopBar: true,
  }),
  newVotingProxyRequest: new RouteConfig({
    id: "newVotingProxyRequest",
    path: "/procuration/donner-ma-procuration/",
    exact: true,
    neededAuthentication: AUTHENTICATION.NONE,
    label: "Donner ma procuration de vote",
    Component: NewVotingProxyRequest,
    hasLayout: false,
    hideFeedbackButton: true,
    hideFooter: true,
    appOnlyTopBar: true,
  }),
  newVotingProxy: new RouteConfig({
    id: "newVotingProxy",
    path: "/procuration/prendre-une-procuration/",
    exact: true,
    neededAuthentication: AUTHENTICATION.NONE,
    label: "Prendre une procuration de vote",
    Component: NewVotingProxy,
    hasLayout: false,
    hideFeedbackButton: true,
    hideFooter: true,
    appOnlyTopBar: true,
  }),
  search: new RouteConfig({
    id: "search",
    path: "/recherche/",
    neededAuthentication: AUTHENTICATION.NONE,
    Component: SearchPage,
    label: "Rechercher",
    hasLayout: false,
    hideFeedbackButton: true,
    hideFooter: true,
  }),
};

export const getRouteByPathname = (pathname) => {
  return Object.values(routeConfig).find(
    (route) => route.path === pathname || route.match(pathname)
  );
};

const routes = Object.values(routeConfig).filter((route) => !route.isPartial);

export default routes;
