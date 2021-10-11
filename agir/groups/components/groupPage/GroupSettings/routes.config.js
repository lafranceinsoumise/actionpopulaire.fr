import { lazy } from "@agir/front/app/utils";
import {
  RouteConfig,
  routeConfig as globalRouteConfig,
} from "@agir/front/app/routes.config";

import illustrationManage from "@agir/front/genericComponents/images/group_members.svg";
import illustrationFinance from "@agir/front/genericComponents/images/group_financement.svg";
import illustrationGeneral from "@agir/front/genericComponents/images/group_general.svg";
import illustrationContact from "@agir/front/genericComponents/images/group_contact.svg";
import illustrationLinks from "@agir/front/genericComponents/images/group_links.svg";

const GroupSettingsMembers = lazy(() =>
  import("@agir/groups/groupPage/GroupSettings/GroupMembersPage")
);
const GroupSettingsContacts = lazy(() =>
  import("@agir/groups/groupPage/GroupSettings/GroupContactsPage")
);
const GroupSettingsManage = lazy(() =>
  import("@agir/groups/groupPage/GroupSettings/GroupManagementPage")
);
const GroupSettingsMateriel = lazy(() =>
  import("@agir/groups/groupPage/GroupSettings/GroupMaterielPage")
);
const GroupSettingsFinance = lazy(() =>
  import("@agir/groups/groupPage/GroupSettings/GroupFinancePage")
);
const GroupSettingsGeneral = lazy(() =>
  import("@agir/groups/groupPage/GroupSettings/GroupGeneralPage")
);
const GroupSettingsLocation = lazy(() =>
  import("@agir/groups/groupPage/GroupSettings/GroupLocalizationPage")
);
const GroupSettingsContact = lazy(() =>
  import("@agir/groups/groupPage/GroupSettings/GroupContactPage")
);
const GroupSettingsLinks = lazy(() =>
  import("@agir/groups/groupPage/GroupSettings/GroupLinksPage")
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
    Component: GroupSettingsMembers,
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
    isActive: true,
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
    isActive: (group) => group?.isReferent || group?.isManager,
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
    label: "Financement",
    icon: "sun",
    Component: GroupSettingsFinance,
    illustration: illustrationFinance,
    isActive: (group) => group?.isCertified,
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
    isActive: true,
    menuGroup: 2,
  },
  location: {
    id: "location",
    path: "localisation/",
    exact: true,
    label: "Localisation",
    icon: "map-pin",
    Component: GroupSettingsLocation,
    isActive: true,
    menuGroup: 2,
  },
  contact: {
    id: "contact",
    path: "contact/",
    exact: true,
    label: "Contact",
    icon: "mail",
    Component: GroupSettingsContact,
    illustration: illustrationContact,
    isActive: true,
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
};

export const getMenuRoute = (basePath) =>
  new RouteConfig({
    ...menuRoute,
    path: basePath + menuRoute.path,
  });

const getActiveRoutes = (group) =>
  Object.values(routeConfig).filter((route) => {
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
        path: basePath + menuRoute.path + route.path,
      })
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
