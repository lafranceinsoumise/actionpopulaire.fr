import { lazy } from "./utils";

const Routes = {
  HomePage: lazy(
    () =>
      import(
        /* webpackChunkName: "r-homepage" */ "@agir/front/app/Homepage/Home"
      ),
  ),
  AgendaPage: lazy(
    () =>
      import(
        /* webpackChunkName: "r-agendapage" */ "@agir/events/agendaPage/Agenda"
      ),
  ),
  EventMap: lazy(
    () =>
      import(
        /* webpackChunkName: "r-eventmap" */ "@agir/carte/page__eventMap/EventMap"
      ),
  ),
  GroupUpcomingEventPage: lazy(
    () =>
      import(
        /* webpackChunkName: "r-groupupcomingevent" */ "@agir/events/groupUpcomingEventPage/GroupUpcomingEventPage"
      ),
  ),
  GroupUpcomingEventRedirectPage: lazy(
    () =>
      import(
        /* webpackChunkName: "r-groupupcomingeventredirect" */ "@agir/events/groupUpcomingEventPage/GroupUpcomingEventRedirectPage"
      ),
  ),
  EventPage: lazy(
    () =>
      import(
        /* webpackChunkName: "r-eventpage" */ "@agir/events/eventPage/EventPage"
      ),
  ),
  MissingDocumentsPage: lazy(
    () =>
      import(
        /* webpackChunkName: "r-missingdocumentspage" */ "@agir/events/eventRequiredDocuments/MissingDocuments/MissingDocumentsPage"
      ),
  ),
  EventRequiredDocuments: lazy(
    () =>
      import(
        /* webpackChunkName: "r-eventrequireddocuments" */ "@agir/events/eventRequiredDocuments/EventRequiredDocumentsPage"
      ),
  ),
  GroupsPage: lazy(
    () =>
      import(
        /* webpackChunkName: "r-groupspage" */ "@agir/groups/groupsPage/GroupsPage"
      ),
  ),
  CreateEvent: lazy(
    () =>
      import(
        /* webpackChunkName: "r-createevent" */ "@agir/events/createEventPage/CreateEvent"
      ),
  ),
  EventRequiredDocuments: lazy(
    () =>
      import(
        /* webpackChunkName: "r-eventrequireddocuments" */ "@agir/events/eventRequiredDocuments/EventRequiredDocumentsPage"
      ),
  ),
  GroupsPage: lazy(
    () =>
      import(
        /* webpackChunkName: "r-groupspage" */ "@agir/groups/groupsPage/GroupsPage"
      ),
  ),
  FullGroupPage: lazy(
    () =>
      import(
        /* webpackChunkName: "r-fullgrouppage" */ "@agir/groups/fullGroupPage/FullGroupPage"
      ),
  ),
  GroupPage: lazy(
    () =>
      import(
        /* webpackChunkName: "r-grouppage" */ "@agir/groups/groupPage/GroupPage"
      ),
  ),
  GroupMessagePage: lazy(
    () =>
      import(
        /* webpackChunkName: "r-groupmessagepage" */ "@agir/groups/groupPage/GroupMessagePage"
      ),
  ),
  GroupMap: lazy(
    () =>
      import(
        /* webpackChunkName: "r-groupmap" */ "@agir/carte/page__groupMap/GroupMap"
      ),
  ),
  ThematicGroups: lazy(
    () =>
      import(
        /* webpackChunkName: "r-thematicgroups" */ "@agir/groups/thematicGroupPage/ThematicGroupPage"
      ),
  ),
  ActivityPage: lazy(
    () =>
      import(
        /* webpackChunkName: "r-activitypage" */ "@agir/activity/ActivityPage/ActivityPage"
      ),
  ),
  NavigationPage: lazy(
    () =>
      import(
        /* webpackChunkName: "r-navigationpage" */ "@agir/front/navigationPage/NavigationPage"
      ),
  ),
  SignupPage: lazy(
    () =>
      import(
        /* webpackChunkName: "r-signuppage" */ "@agir/front/authentication/Connexion/SignupPage"
      ),
  ),
  LoginPage: lazy(
    () =>
      import(
        /* webpackChunkName: "r-loginpage" */ "@agir/front/authentication/Connexion/LoginPage"
      ),
  ),
  CodeLoginPage: lazy(
    () =>
      import(
        /* webpackChunkName: "r-codeloginpage" */ "@agir/front/authentication/Connexion/Code/CodeLogin"
      ),
  ),
  CodeSignupPage: lazy(
    () =>
      import(
        /* webpackChunkName: "r-codesignuppage" */ "@agir/front/authentication/Connexion/Code/CodeSignup"
      ),
  ),
  TellMorePage: lazy(
    () =>
      import(
        /* webpackChunkName: "r-tellmorepage" */ "@agir/front/authentication/Connexion/TellMore/TellMorePage"
      ),
  ),
  LogoutPage: lazy(
    () =>
      import(
        /* webpackChunkName: "r-logoutpage" */ "@agir/front/authentication/Connexion/Logout"
      ),
  ),
  MessagePage: lazy(
    () =>
      import(
        /* webpackChunkName: "r-messagepage" */ "@agir/msgs/MessagePage/MessagePage"
      ),
  ),
  CreateContactPage: lazy(
    () =>
      import(
        /* webpackChunkName: "r-createcontactpage" */ "@agir/people/contacts/CreateContactPage"
      ),
  ),
  DonationLandingPage: lazy(
    () =>
      import(
        /* webpackChunkName: "r-donationlandingpage" */ "@agir/donations/DonationLandingPage"
      ),
  ),
  DonationPage: lazy(
    () =>
      import(
        /* webpackChunkName: "r-donationpage" */ "@agir/donations/donationPage/DonationPage"
      ),
  ),
  ExternalDonationPage: lazy(
    () =>
      import(
        /* webpackChunkName: "r-externalDonationPage" */ "@agir/donations/externalDonationPage/ExternalDonationPage"
      ),
  ),
  DonationSuccessPage: lazy(
    () =>
      import(
        /* webpackChunkName: "r-donationSuccessPage" */ "@agir/donations/donationSuccessPage/DonationSuccessPage"
      ),
  ),
  ContributionPage: lazy(
    () =>
      import(
        /* webpackChunkName: "r-contributionpage" */ "@agir/donations/contributionPage/ContributionPage"
      ),
  ),
  ContributionSuccessPage: lazy(
    () =>
      import(
        /* webpackChunkName: "r-contributionSuccessPage" */ "@agir/donations/contributionSuccessPage/ContributionSuccessPage"
      ),
  ),
  ContributionRenewalPage: lazy(
    () =>
      import(
        /* webpackChunkName: "r-contributionrenewalpage" */ "@agir/donations/contributionRenewalPage/ContributionRenewalPage"
      ),
  ),
  ActionToolsPage: lazy(
    () =>
      import(
        /* webpackChunkName: "r-actiontoolspage" */ "@agir/front/ActionToolsPage/ActionToolsPage"
      ),
  ),
  SearchPage: lazy(
    () =>
      import(
        /* webpackChunkName: "r-searchpage" */ "@agir/front/SearchPage/SearchPage"
      ),
  ),
  SearchGroupPage: lazy(
    () =>
      import(
        /* webpackChunkName: "r-searchgrouppage" */ "@agir/front/SearchPage/SearchGroupPage"
      ),
  ),
  SearchEventPage: lazy(
    () =>
      import(
        /* webpackChunkName: "r-searcheventpage" */ "@agir/front/SearchPage/SearchEventPage"
      ),
  ),
  NewVotingProxyRequest: lazy(
    () =>
      import(
        /* webpackChunkName: "r-newvotingproxyrequest" */ "@agir/voting_proxies/VotingProxyRequest/NewVotingProxyRequest"
      ),
  ),
  NewVotingProxy: lazy(
    () =>
      import(
        /* webpackChunkName: "r-newvotingproxy" */ "@agir/voting_proxies/VotingProxy/NewVotingProxy"
      ),
  ),
  ReplyToVotingProxyRequests: lazy(
    () =>
      import(
        /* webpackChunkName: "r-replytovotingproxyrequests" */ "@agir/voting_proxies/VotingProxy/ReplyToVotingProxyRequests"
      ),
  ),
  VotingProxyRequestDetails: lazy(
    () =>
      import(
        /* webpackChunkName: "r-votingproxyrequestdetails" */ "@agir/voting_proxies/VotingProxyRequest/VotingProxyRequestDetails"
      ),
  ),
  TestErrorPage: lazy(
    () =>
      import(
        /* webpackChunkName: "r-testerrorpage" */ "@agir/front/errorPage/TestErrorPage"
      ),
  ),
  TokTokPreview: lazy(
    () =>
      import(
        /* webpackChunkName: "r-toktokpreview" */ "@agir/events/TokTok/TokTokPreview"
      ),
  ),
  NewPollingStationOfficer: lazy(
    () =>
      import(
        /* webpackChunkName: "r-newpollingstationofficer" */ "@agir/elections/PollingStationOfficer/NewPollingStationOfficer"
      ),
  ),
  EventSpeakerPage: lazy(
    () =>
      import(
        /* webpackChunkName: "r-eventspeakerpage" */ "@agir/event_requests/EventSpeakerPage/EventSpeakerPage"
      ),
  ),
  FaIcons: lazy(
    () =>
      import(
        /* webpackChunkName: "r-faicons" */ "@agir/front/genericComponents/FaIcons"
      ),
  ),
  CreateSpendingRequest: lazy(
    () =>
      import(
        /* webpackChunkName: "r-createspendingrequest" */ "@agir/donations/spendingRequest/createSpendingRequestPage"
      ),
  ),
  EditSpendingRequest: lazy(
    () =>
      import(
        /* webpackChunkName: "r-editspendingrequest" */ "@agir/donations/spendingRequest/editSpendingRequestPage"
      ),
  ),
  SpendingRequestDetails: lazy(
    () =>
      import(
        /* webpackChunkName: "r-spendingrequestdetails" */ "@agir/donations/spendingRequest/spendingRequestPage"
      ),
  ),
  SpendingRequestHistory: lazy(
    () =>
      import(
        /* webpackChunkName: "r-spendingrequesthistory" */ "@agir/donations/spendingRequest/spendingRequestPage/SpendingRequestHistoryPage"
      ),
  ),
};

export default Routes;
