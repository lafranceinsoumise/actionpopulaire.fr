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
  import("@agir/groups/groupPage/GroupSettings/GroupMemberPage")
);
const GroupSettingsManage = lazy(() =>
  import("@agir/groups/groupPage/GroupSettings/GroupManagementPage")
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
    label: "Membres",
    icon: "users",
    Component: GroupSettingsMembers,
  },
  manage: {
    id: "manage",
    path: "animation/",
    exact: true,
    label: "Gestion et animation",
    icon: "lock",
    Component: GroupSettingsManage,
    illustration: illustrationManage,
  },
  finance: {
    id: "finance",
    path: "finance/",
    exact: true,
    label: "Financement",
    icon: "sun",
    Component: GroupSettingsFinance,
    illustration: illustrationFinance,
  },
  general: {
    id: "general",
    path: "general/",
    exact: true,
    label: "Général",
    icon: "file-text",
    Component: GroupSettingsGeneral,
    illustration: illustrationGeneral,
  },
  location: {
    id: "location",
    path: "localisation/",
    exact: true,
    label: "Localisation",
    icon: "map-pin",
    Component: GroupSettingsLocation,
  },
  contact: {
    id: "contact",
    path: "contact/",
    exact: true,
    label: "Contact",
    icon: "mail",
    Component: GroupSettingsContact,
    illustration: illustrationContact,
  },
  links: {
    id: "links",
    path: "liens/",
    exact: true,
    label: "Liens et réseaux sociaux",
    icon: "at-sign",
    Component: GroupSettingsLinks,
    illustration: illustrationLinks,
  },
};

export const getMenuRoute = (basePath) =>
  new RouteConfig({
    ...menuRoute,
    path: basePath + menuRoute.path,
  });

export const getRoutes = (basePath) =>
  Object.values(routeConfig).reduce(
    (result, route) => [
      ...result,
      new RouteConfig({
        ...route,
        path: basePath + menuRoute.path + route.path,
      }),
    ],
    []
  );

export const getGroupSettingLinks = (groupPk) => {
  const links = {};
  if (!groupPk) {
    return links;
  }
  Object.values(routeConfig).forEach((route) => {
    links[route.id] = globalRouteConfig.groupSettings.getLink({
      activePanel: route.path.replace("/", "") || null,
      groupPk,
    });
  });
  return links;
};

export default getRoutes;
