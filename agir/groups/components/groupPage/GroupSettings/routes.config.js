import { lazy } from "@agir/front/app/utils";
import {
  RouteConfig,
  routeConfig as globalRouteConfig,
} from "@agir/front/app/routes.config";

import illustrationManage from "@agir/front/genericComponents/images/group_members.svg";
import illustrationFinance from "@agir/front/genericComponents/images/group_financement.svg";
import illustrationUpcomingEvents from "@agir/front/genericComponents/images/group_agenda.svg";
import illustrationGeneral from "@agir/front/genericComponents/images/group_general.svg";
import illustrationContact from "@agir/front/genericComponents/images/group_contact.svg";
import illustrationLinks from "@agir/front/genericComponents/images/group_links.svg";
import illustrationHelp from "@agir/front/genericComponents/images/group_help.svg";
import illustrationStats from "@agir/front/genericComponents/images/group_stats.svg";

const GroupSettingsReadOnlyMembers = lazy(
  () =>
    import(
      /* webpackChunkName: "r-groupsettingsreadonlymembers" */ "@agir/groups/groupPage/GroupSettings/GroupReadOnlyMembersPage"
    ),
);
const GroupSettingsActiveMembers = lazy(
  () =>
    import(
      /* webpackChunkName: "r-groupsettingsactivemembers" */ "@agir/groups/groupPage/GroupSettings/GroupActiveMembersPage"
    ),
);
const GroupSettingsContacts = lazy(
  () =>
    import(
      /* webpackChunkName: "r-groupsettingscontacts" */ "@agir/groups/groupPage/GroupSettings/GroupContactsPage"
    ),
);
const GroupSettingsManage = lazy(
  () =>
    import(
      /* webpackChunkName: "r-groupsettingsmanage" */ "@agir/groups/groupPage/GroupSettings/GroupManagementPage"
    ),
);
const GroupSettingsMateriel = lazy(
  () =>
    import(
      /* webpackChunkName: "r-groupsettingsmateriel" */ "@agir/groups/groupPage/GroupSettings/GroupMaterielPage"
    ),
);
const GroupSettingsUpcomingEvents = lazy(
  () =>
    import(
      /* webpackChunkName: "r-groupsettingsupcomingevents" */ "@agir/groups/groupPage/GroupSettings/GroupUpcomingEventPage"
    ),
);
const GroupSettingsFinance__Group = lazy(
  () =>
    import(
      /* webpackChunkName: "r-groupsettingsfinancegroup" */ "@agir/groups/groupPage/GroupSettings/GroupFinancePage/Group"
    ),
);
const GroupSettingsFinance__BouDep = lazy(
  () =>
    import(
      /* webpackChunkName: "r-groupsettingsfinanceboudep" */ "@agir/groups/groupPage/GroupSettings/GroupFinancePage/BouDep"
    ),
);
const GroupSettingsGeneral = lazy(
  () =>
    import(
      /* webpackChunkName: "r-groupsettingsgeneral" */ "@agir/groups/groupPage/GroupSettings/GroupGeneralPage"
    ),
);
const GroupSettingsLocation = lazy(
  () =>
    import(
      /* webpackChunkName: "r-groupsettingslocation" */ "@agir/groups/groupPage/GroupSettings/GroupLocalizationPage"
    ),
);
const GroupSettingsContact = lazy(
  () =>
    import(
      /* webpackChunkName: "r-groupsettingscontact" */ "@agir/groups/groupPage/GroupSettings/GroupContactPage"
    ),
);
const GroupSettingsLinks = lazy(
  () =>
    import(
      /* webpackChunkName: "r-groupsettingslinks" */ "@agir/groups/groupPage/GroupSettings/GroupLinksPage"
    ),
);
const GroupSettingsCertification = lazy(
  () =>
    import(
      /* webpackChunkName: "r-groupsettingscertification" */ "@agir/groups/groupPage/GroupSettings/GroupCertificationPage"
    ),
);
const GroupSettingsHelp = lazy(
  () =>
    import(
      /* webpackChunkName: "r-groupsettingshelp" */ "@agir/groups/groupPage/GroupSettings/GroupHelpPage"
    ),
);
const GroupSettingsStats = lazy(
  () =>
    import(
      /* webpackChunkName: "r-groupsettingsstats" */ "@agir/groups/groupPage/GroupSettings/GroupStatisticsPage"
    ),
);

export const menuRoute = {
  id: "menu",
  path: "gestion/",
  exact: false,
  label: "Paramètres du groupe",
};

export const routeConfig = {
  members: {
    id: "members",
    path: "membres/",
    exact: true,
    label: "Membres actifs",
    icon: "users",
    getComponent: (group) =>
      group.isEditable
        ? GroupSettingsActiveMembers
        : GroupSettingsReadOnlyMembers,
    isActive: true,
    menuGroup: 1,
  },
  stats: {
    id: "stats",
    path: "statistiques/",
    exact: true,
    label: "Statistiques",
    icon: "trello",
    Component: GroupSettingsStats,
    illustration: illustrationStats,
    isActive: true,
    menuGroup: 1,
  },
  contacts: {
    id: "contacts",
    path: "contacts/",
    exact: true,
    label: "Contacts",
    icon: "rss",
    Component: GroupSettingsContacts,
    isActive: (group) => group.isEditable,
    menuGroup: 1,
  },
  manage: {
    id: "manage",
    path: "animation/",
    exact: true,
    label: "Gestion et animation",
    icon: "lock",
    Component: GroupSettingsManage,
    illustration: illustrationManage,
    isActive: (group) => group.isEditable,
    menuGroup: 1,
  },
  certification: {
    id: "certification",
    path: "certification/",
    exact: true,
    label: "Certification",
    icon: "check-circle",
    Component: GroupSettingsCertification,
    isActive: (group) => group.isCertifiable || group.isCertified,
    menuGroup: 1,
  },
  materiel: {
    id: "materiel",
    path: "materiel/",
    exact: true,
    label: "Matériel",
    icon: "shopping-bag",
    Component: GroupSettingsMateriel,
    isActive: (group) =>
      Array.isArray(group.discountCodes) && group.discountCodes.length > 0,
    menuGroup: 1,
  },
  finance: {
    id: "finance",
    path: "finance/",
    exact: true,
    label: (group) =>
      group.isBoucleDepartementale ? "Caisse de la boucle" : "Caisse du groupe",
    icon: "briefcase",
    getComponent: (group) =>
      group.isBoucleDepartementale
        ? GroupSettingsFinance__BouDep
        : GroupSettingsFinance__Group,
    illustration: illustrationFinance,
    isActive: (group) => group.isFinanceable && group.isFinanceManager,
    menuGroup: 1,
  },
  upcomingEvents: {
    id: "upcomingEvents",
    path: "agenda/",
    exact: true,
    label: "Agenda",
    icon: "calendar",
    Component: GroupSettingsUpcomingEvents,
    illustration: illustrationUpcomingEvents,
    isActive: true,
    menuGroup: 1,
  },
  general: {
    id: "general",
    path: "general/",
    exact: true,
    label: "Général",
    icon: "file-text",
    Component: GroupSettingsGeneral,
    illustration: illustrationGeneral,
    isActive: (group) => group.isEditable,
    menuGroup: 2,
  },
  location: {
    id: "location",
    path: "localisation/",
    exact: true,
    label: "Localisation",
    icon: "map-pin",
    Component: GroupSettingsLocation,
    isActive: (group) => group.isEditable,
    menuGroup: 2,
  },
  contact: {
    id: "contact",
    path: "contact/",
    exact: true,
    label: "Moyens de contact",
    icon: "mail",
    Component: GroupSettingsContact,
    illustration: illustrationContact,
    isActive: (group) => group.isEditable,
    menuGroup: 2,
  },
  links: {
    id: "links",
    path: "liens/",
    exact: true,
    label: "Liens et réseaux sociaux",
    icon: "at-sign",
    Component: GroupSettingsLinks,
    illustration: illustrationLinks,
    isActive: true,
    menuGroup: 2,
  },
  help: {
    id: "help",
    path: "ressources/",
    exact: true,
    label: "Ressources",
    icon: "more-horizontal",
    Component: GroupSettingsHelp,
    illustration: illustrationHelp,
    isActive: true,
    menuGroup: 3,
  },
};

export const getMenuRoute = (basePath) =>
  new RouteConfig({
    ...menuRoute,
    path: basePath + menuRoute.path,
  });

const getActiveRoutes = (group) =>
  Object.values(routeConfig).filter((route) => {
    if (!group || !group.isManager) {
      return false;
    }
    if (typeof route.isActive === "function") {
      return !!route.isActive(group);
    }
    return !!route.isActive;
  });

export const getRoutes = (basePath, group) =>
  getActiveRoutes(group).map(
    (route) =>
      new RouteConfig({
        ...route,
        label:
          typeof route.label === "function" ? route.label(group) : route.label,
        Component:
          typeof route.getComponent === "function"
            ? route.getComponent(group)
            : route.Component,
        path: basePath + menuRoute.path + route.path,
      }),
  );

export const getGroupSettingLinks = (group, basePath) => {
  const links = {};

  if (!group?.id || !group.isManager) {
    return links;
  }

  if (!basePath) {
    const activeRoutes = getActiveRoutes(group);
    links.menu = globalRouteConfig.groupSettings.getLink({
      groupPk: group.id,
    });
    activeRoutes.forEach((route) => {
      links[route.id] = globalRouteConfig.groupSettings.getLink({
        activePanel: route.path.replace("/", "") || null,
        groupPk: group.id,
      });
    });
    return links;
  }

  const activeRoutes = getRoutes(basePath, group);
  links.menu = getMenuRoute(basePath).getLink();
  activeRoutes.forEach((route) => {
    links[route.id] = route.getLink();
  });

  return links;
};

export default getRoutes;
