import React from "react";
import GroupMemberPage from "./GroupMemberPage.js";
import GroupManagementPage from "./GroupManagementPage.js";
import GroupFinancePage from "./GroupFinancePage.js";
import GroupGeneralPage from "./GroupGeneralPage.js";
import GroupLocalizationPage from "./GroupLocalizationPage.js";
import GroupContactPage from "./GroupContactPage.js";
import GroupLinksPage from "./GroupLinksPage.js";

import group_members from "@agir/front/genericComponents/images/group_members.svg";
import group_financement from "@agir/front/genericComponents/images/group_financement.svg";
import group_general from "@agir/front/genericComponents/images/group_general.svg";
import group_contact from "@agir/front/genericComponents/images/group_contact.svg";
import group_links from "@agir/front/genericComponents/images/group_links.svg";

import { routeConfig } from "@agir/front/app/routes.config";

export const DEFAULT_GROUP = {
  title: "Cortège France insoumise à la marche contre la fourrure 2020",
  // membersCount: 3,
};

export const DEFAULT_EMAILS = [
  "test@example.fr",
  "test@example.fr",
  "test@example.fr",
];

export const DEFAULT_MEMBERS = [
  {
    name: "Jean-Luc Mélenchon",
    role: "Administrateur",
    email: "jlm@email.fr",
    assets: ["Député", "Journaliste", "Blogueur", "Artiste", "Informaticien"],
  },
  {
    name: "Membre",
    role: "Animatrice",
    email: "example@email.fr",
    assets: ["Journaliste", "Blogueur", "Artiste"],
  },
  {
    name: "Membre",
    role: "Animatrice",
    email: "example@email.fr",
    assets: ["Journaliste", "Blogueur", "Artiste"],
  },
];

export const MENU_ITEMS_GROUP = {
  members: {
    id: "members",
    label: "Membres",
    icon: "users",
    component: <GroupMemberPage />,
    route: "groupSettingsMembers",
    // route: routeConfig.groupSettingsMembers.getLink(),
  },
  management: {
    id: "management",
    label: "Gestion et animation",
    icon: "lock",
    illustration: group_members,
    component: <GroupManagementPage />,
    route: "groupSettingsManage",
    // route: routeConfig.groupSettingsManage.getLink(),
  },
  finance: {
    id: "finance",
    label: "Financement",
    icon: "sun",
    illustration: group_financement,
    component: <GroupFinancePage />,
    route: "groupSettingsFinance",
    // route: routeConfig.groupSettingsFinance.getLink(),
  },
  general: {
    id: "general",
    label: "Général",
    icon: "file-text",
    illustration: group_general,
    component: <GroupGeneralPage />,
    route: "groupSettingsGeneral",
    // route: routeConfig.groupSettingsGeneral.getLink(),
  },
  location: {
    id: "location",
    label: "Localisation",
    icon: "map-pin",
    component: <GroupLocalizationPage />,
    route: "groupSettingsLocation",
    // route: routeConfig.groupSettingsLocation.getLink(),
  },
  contact: {
    id: "contact",
    label: "Contact",
    icon: "mail",
    illustration: group_contact,
    component: <GroupContactPage />,
    route: "groupSettingsContact",
    // route: routeConfig.groupSettingsContact.getLink(),
  },
  links: {
    id: "links",
    label: "Liens et réseaux sociaux",
    icon: "at-sign",
    illustration: group_links,
    component: <GroupLinksPage />,
    route: "groupSettingsLinks",
    // route: routeConfig.groupSettingsLinks.getLink(),
  },
};
