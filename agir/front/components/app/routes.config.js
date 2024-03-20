import pathToRegexp from "path-to-regexp-es";

import style from "@agir/front/genericComponents/_variables.scss";
import logger from "@agir/lib/utils/logger";

import { AUTHENTICATION } from "@agir/front/authentication/common";
import { relativeToAbsoluteURL } from "@agir/lib/utils/url";

import RouteComponents from "./routes.components";
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
   * @param  {absolute} absolute Whether to return an absolute or relative link
   * @return {string} The link path string
   */
  getLink(params, absolute = false) {
    try {
      params = {
        ...(this.params || {}),
        ...(params || {}),
      };
      const link = this.__toPath__(params);
      return absolute ? relativeToAbsoluteURL(link) : link;
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
    path: "/",
    exact: true,
    neededAuthentication: AUTHENTICATION.SOFT,
    label: "Liste des événements",
    Component: RouteComponents.AgendaPage,
    hasLayout: true,
    layoutProps: {
      $smallBackgroundColor: style.black25,
    },
    hideFeedbackButton: true,
    keepScroll: true,
    hideFooterBanner: true,
    AnonymousComponent: RouteComponents.HomePage,
    anonymousConfig: {
      hasLayout: false,
    },
  }),
  eventMap: new RouteConfig({
    id: "eventMap",
    path: "/evenements/carte/",
    exact: true,
    neededAuthentication: AUTHENTICATION.NONE,
    label: "Carte des événements",
    Component: RouteComponents.EventMap,
    hideFooter: true,
    hideFeedbackButton: true,
  }),
  mapEventDetails: new RouteConfig({
    id: "mapEventDetails",
    path: "/evenements/carte/:eventPk/",
    exact: true,
    neededAuthentication: AUTHENTICATION.NONE,
    label: "Carte des événements",
    redirectTo: (_, routeParams) => ({
      route: "eventDetails",
      routeParams,
      backLink: "eventMap",
      push: false,
    }),
  }),
  groupUpcomingEventRedirect: new RouteConfig({
    id: "groupUpcomingEventRedirect",
    path: "/evenements/groupes/:groupPk/",
    exact: true,
    neededAuthentication: AUTHENTICATION.SOFT,
    label: "Agenda des groupes d'action",
    Component: RouteComponents.GroupUpcomingEventRedirectPage,
  }),
  groupUpcomingEvents: new RouteConfig({
    id: "groupUpcomingEvents",
    path: "/evenements/groupes/",
    exact: true,
    neededAuthentication: AUTHENTICATION.SOFT,
    label: "Agenda des groupes d'action",
    Component: RouteComponents.GroupUpcomingEventPage,
  }),
  createEvent: new RouteConfig({
    id: "createEvent",
    path: "/evenements/creer/",
    exact: false,
    neededAuthentication: AUTHENTICATION.SOFT,
    label: "Nouvel événement",
    hideFeedbackButton: true,
    Component: RouteComponents.CreateEvent,
    hideFooter: true,
  }),
  eventSettings: new RouteConfig({
    id: "eventSettings",
    path: "/evenements/:eventPk/gestion/:activePanel?/",
    params: { eventPk: null, activePanel: null },
    exact: true,
    isPartial: true,
    neededAuthentication: AUTHENTICATION.HARD,
    Component: RouteComponents.EventPage,
    hideFeedbackButton: true,
  }),
  eventSpeaker: new RouteConfig({
    id: "eventSpeaker",
    path: "/evenements/demandes/intervenant-e/",
    exact: true,
    neededAuthentication: AUTHENTICATION.SOFT,
    label: "Demandes d'événements",
    Component: RouteComponents.EventSpeakerPage,
    hasLayout: false,
    hideFeedbackButton: true,
  }),
  eventDetails: new RouteConfig({
    id: "eventDetails",
    path: "/evenements/:eventPk/",
    exact: false,
    neededAuthentication: AUTHENTICATION.NONE,
    label: "Page de l'événement",
    Component: RouteComponents.EventPage,
  }),
  groups: new RouteConfig({
    id: "groups",
    path: "/mes-groupes/",
    exact: true,
    neededAuthentication: AUTHENTICATION.SOFT,
    label: "Liste des groupes",
    Component: RouteComponents.GroupsPage,
    hasLayout: true,
    layoutProps: {
      $smallBackgroundColor: style.black25,
    },
    keepScroll: true,
  }),
  groupMap: new RouteConfig({
    id: "groupMap",
    path: "/groupes/carte/",
    exact: true,
    neededAuthentication: AUTHENTICATION.NONE,
    label: "Carte des groupes",
    Component: RouteComponents.GroupMap,
    hideFooter: true,
    hideFeedbackButton: true,
  }),
  mapGroupDetails: new RouteConfig({
    id: "mapGroupDetails",
    path: "/groupes/carte/:groupPk/",
    exact: true,
    neededAuthentication: AUTHENTICATION.NONE,
    redirectTo: (_, routeParams) => ({
      route: "groupDetails",
      routeParams,
      backLink: "groupMap",
      push: false,
    }),
  }),
  fullGroup: new RouteConfig({
    id: "fullGroup",
    path: "/groupes/:groupPk/complet/",
    exact: true,
    neededAuthentication: AUTHENTICATION.NONE,
    label: "Groupe complet",
    Component: RouteComponents.FullGroupPage,
    hasLayout: false,
  }),
  groupSettings: new RouteConfig({
    id: "groupSettings",
    path: "/groupes/:groupPk/:activeTab?/gestion/:activePanel?/",
    params: { activeTab: null, activePanel: null },
    exact: true,
    neededAuthentication: AUTHENTICATION.HARD,
    Component: RouteComponents.GroupPage,
    isPartial: true,
  }),
  createGroupSpendingRequest: new RouteConfig({
    id: "createGroupSpendingRequest",
    path: "/groupes/:groupPk/depenses/creer/",
    exact: true,
    neededAuthentication: AUTHENTICATION.HARD,
    label: "Nouvelle dépense",
    Component: RouteComponents.CreateSpendingRequest,
    hideFeedbackButton: true,
    backLink: {
      label: "Gestion du groupe",
      route: "groupSettings",
      routeParams: {
        activePanel: "finance",
      },
    },
  }),
  groupDetails: new RouteConfig({
    id: "groupDetails",
    path: "/groupes/:groupPk/:activeTab?/",
    exact: false,
    neededAuthentication: AUTHENTICATION.NONE,
    label: "Page du groupe",
    Component: RouteComponents.GroupPage,
    backLink: {
      route: "groups",
      isProtected: true,
    },
  }),
  thematicGroups: new RouteConfig({
    id: "thematicGroups",
    path: "/groupes-thematiques/",
    exact: true,
    neededAuthentication: AUTHENTICATION.NONE,
    label: "Les groupes thématiques",
    Component: RouteComponents.ThematicGroups,
  }),
  spendingRequestDetails: new RouteConfig({
    id: "spendingRequestDetails",
    path: "/financement/demande/:spendingRequestPk/",
    exact: true,
    neededAuthentication: AUTHENTICATION.HARD,
    label: "Détails de la demande",
    Component: RouteComponents.SpendingRequestDetails,
  }),
  spendingRequestHistory: new RouteConfig({
    id: "spendingRequestDetails",
    path: "/financement/demande/:spendingRequestPk/historique/",
    exact: true,
    neededAuthentication: AUTHENTICATION.HARD,
    label: "Historique de la demande",
    Component: RouteComponents.SpendingRequestHistory,
    backLink: {
      label: "Détails de la demande",
      route: "spendingRequestDetails",
    },
  }),
  editSpendingRequest: new RouteConfig({
    id: "editGroupSpendingRequest",
    path: "/financement/demande/:spendingRequestPk/modifier/",
    exact: true,
    neededAuthentication: AUTHENTICATION.HARD,
    label: "Modification de la dépense",
    Component: RouteComponents.EditSpendingRequest,
    hideFeedbackButton: true,
    backLink: {
      label: "Détail de la demande",
      route: "spendingRequestDetails",
    },
  }),
  activities: new RouteConfig({
    id: "activities",
    path: ["/activite/", "/activite/parametres/"],
    exact: true,
    neededAuthentication: AUTHENTICATION.SOFT,
    label: "Notifications",
    Component: RouteComponents.ActivityPage,
    hasLayout: true,
    layoutProps: {
      $smallBackgroundColor: style.black25,
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
    Component: RouteComponents.ActionToolsPage,
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
    Component: RouteComponents.NavigationPage,
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
    Component: RouteComponents.LoginPage,
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
    Component: RouteComponents.SignupPage,
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
    Component: RouteComponents.CodeLoginPage,
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
    Component: RouteComponents.CodeSignupPage,
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
    Component: RouteComponents.TellMorePage,
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
    Component: RouteComponents.LogoutPage,
  }),
  messages: new RouteConfig({
    id: "messages",
    path: ["/messages/:messagePk?/", "/messages/:messagePk/parametres/"],
    params: { messagePk: null },
    exact: true,
    neededAuthentication: AUTHENTICATION.HARD,
    label: "Messages",
    Component: RouteComponents.MessagePage,
    hasLayout: false,
    hideFeedbackButton: true,
    hideFooter: true,
    topBarRightLink: {
      messageSettings: true,
    },
  }),
  createContact: new RouteConfig({
    id: "createContact",
    path: "/contacts/creer/:step?/",
    params: { step: null },
    exact: true,
    neededAuthentication: AUTHENTICATION.SOFT,
    label: "Nouveau contact",
    Component: RouteComponents.CreateContactPage,
    hasLayout: false,
    hideFeedbackButton: true,
    hideFooter: true,
  }),
  donationLanding: new RouteConfig({
    id: "donationLanding",
    path: "/financer/",
    exact: true,
    neededAuthentication: AUTHENTICATION.NONE,
    label: "Financer",
    Component: RouteComponents.DonationLandingPage,
    hasLayout: false,
    hideFeedbackButton: true,
    hideFooter: true,
    appOnlyTopBar: true,
  }),
  donationSuccess: new RouteConfig({
    id: "donationSuccess",
    params: { type: null },
    path: "/:type?/dons/remerciement/",
    exact: true,
    neededAuthentication: AUTHENTICATION.NONE,
    label: "Faire un don",
    Component: RouteComponents.DonationSuccessPage,
    hasLayout: false,
    hideFeedbackButton: true,
    hideFooter: true,
    appOnlyTopBar: true,
  }),
  externalDonation: new RouteConfig({
    id: "externalDonation",
    params: { type: null },
    path: ["/:type?/dons/informations/", "/:type?/dons-mensuels/informations/"],
    exact: true,
    neededAuthentication: AUTHENTICATION.NONE,
    label: "Faire un don",
    Component: RouteComponents.ExternalDonationPage,
    hasLayout: false,
    hideFeedbackButton: true,
    hideFooter: true,
    appOnlyTopBar: true,
  }),
  donations: new RouteConfig({
    id: "donations",
    path: "/:type?/dons/:step?/",
    params: { type: null, step: null },
    exact: true,
    neededAuthentication: AUTHENTICATION.NONE,
    label: "Faire un don",
    Component: RouteComponents.DonationPage,
    hasLayout: false,
    hideFeedbackButton: true,
    hideFooter: true,
    appOnlyTopBar: true,
  }),
  contributionSuccess: new RouteConfig({
    id: "contributionSuccess",
    path: "/contributions/remerciement/",
    exact: true,
    neededAuthentication: AUTHENTICATION.NONE,
    label: "Devenir financeur·euse de la France insoumise",
    Component: RouteComponents.ContributionSuccessPage,
    hasLayout: false,
    hideFeedbackButton: true,
    hideFooter: true,
    appOnlyTopBar: true,
  }),
  contributionRenewal: new RouteConfig({
    id: "contributionRenewal",
    path: "/contributions/renouvelement/",
    exact: true,
    neededAuthentication: AUTHENTICATION.HARD,
    label: "Renouveler le financement à la France insoumise",
    Component: RouteComponents.ContributionRenewalPage,
    hasLayout: false,
    hideFeedbackButton: true,
  }),
  contributions: new RouteConfig({
    id: "contributions",
    path: "/contributions/:step?/",
    params: { step: null },
    exact: true,
    neededAuthentication: AUTHENTICATION.NONE,
    label: "Devenir financeur·euse de la France insoumise",
    Component: RouteComponents.ContributionPage,
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
    Component: RouteComponents.NewVotingProxyRequest,
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
    Component: RouteComponents.NewVotingProxy,
    hasLayout: false,
    hideFeedbackButton: true,
    hideFooter: true,
    appOnlyTopBar: true,
  }),
  replyToVotingProxyRequests: new RouteConfig({
    id: "replyToVotingProxyRequests",
    path: "/procuration/prendre-une-procuration/:votingProxyPk/",
    params: { votingProxyPk: null },
    exact: true,
    neededAuthentication: AUTHENTICATION.NONE,
    label: "Prendre une procuration de vote",
    Component: RouteComponents.ReplyToVotingProxyRequests,
    hasLayout: false,
    hideFeedbackButton: true,
    hideFooter: true,
    appOnlyTopBar: true,
  }),
  acceptedVotingProxyRequests: new RouteConfig({
    id: "acceptedVotingProxyRequests",
    path: "/procuration/prendre-une-procuration/:votingProxyPk/demandes/",
    params: { votingProxyPk: null },
    exact: true,
    neededAuthentication: AUTHENTICATION.NONE,
    label: "Prendre une procuration de vote",
    Component: RouteComponents.ReplyToVotingProxyRequests,
    hasLayout: false,
    hideFeedbackButton: true,
    hideFooter: true,
    appOnlyTopBar: true,
  }),
  votingProxyRequestDetails: new RouteConfig({
    id: "votingProxyRequestDetails",
    path: "/procuration/reponse/",
    exact: true,
    neededAuthentication: AUTHENTICATION.NONE,
    label: "Procuration de vote",
    Component: RouteComponents.VotingProxyRequestDetails,
    hasLayout: false,
    hideFeedbackButton: true,
    hideFooter: true,
    appOnlyTopBar: true,
  }),
  search: new RouteConfig({
    id: "search",
    path: "/recherche/",
    exact: true,
    neededAuthentication: AUTHENTICATION.NONE,
    Component: RouteComponents.SearchPage,
    label: "Rechercher",
    hasLayout: false,
    hideFeedbackButton: true,
  }),
  searchGroup: new RouteConfig({
    id: "searchGroup",
    path: "/recherche/groupes/",
    neededAuthentication: AUTHENTICATION.NONE,
    Component: RouteComponents.SearchGroupPage,
    label: "Rechercher un groupe",
    hasLayout: false,
    hideFeedbackButton: true,
  }),
  searchEvent: new RouteConfig({
    id: "searchEvent",
    path: "/recherche/evenements/",
    neededAuthentication: AUTHENTICATION.NONE,
    Component: RouteComponents.SearchEventPage,
    label: "Rechercher un événement",
    hasLayout: false,
    hideFeedbackButton: true,
  }),
  testErrorPage: new RouteConfig({
    id: "testErrorPage",
    path: "/500/",
    neededAuthentication: AUTHENTICATION.NONE,
    Component: RouteComponents.TestErrorPage,
    label: "Une erreur est survenue",
    hideFeedbackButton: true,
    hideFooter: true,
  }),
  toktokPreview: new RouteConfig({
    id: "toktokPreview",
    path: "/toktok/",
    exact: true,
    neededAuthentication: AUTHENTICATION.SOFT,
    label: "TokTok",
    Component: RouteComponents.TokTokPreview,
    hasLayout: false,
    hideFeedbackButton: true,
    hideFooter: true,
  }),
  newPollingStationOfficer: new RouteConfig({
    id: "newPollingStationOfficer",
    path: "/elections/assesseures-deleguees/",
    exact: true,
    neededAuthentication: AUTHENTICATION.NONE,
    label: "Devenir assesseur·e ou délégué·e",
    Component: RouteComponents.NewPollingStationOfficer,
    hasLayout: false,
    hideFeedbackButton: true,
    hideFooter: true,
    appOnlyTopBar: true,
  }),
  faIcons: new RouteConfig({
    id: "faIcons",
    path: "/test/fontawesome/",
    exact: true,
    neededAuthentication: AUTHENTICATION.NONE,
    label: "Icônes Font Awesome",
    Component: RouteComponents.FaIcons,
    hideFeedbackButton: true,
  }),
};

export const getRouteByPathname = (pathname) => {
  return Object.values(routeConfig).find(
    (route) => route.path === pathname || route.match(pathname),
  );
};

const routes = Object.values(routeConfig).filter((route) => !route.isPartial);

export default routes;
