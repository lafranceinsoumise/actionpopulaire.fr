import React from "react";
import GroupMemberPage from "./GroupMemberPage.js";
import GroupManagementPage from "./GroupManagementPage.js";
import GroupFinancePage from "./GroupFinancePage.js";

import group_members from "@agir/front/genericComponents/images/group_members.svg";
import group_financement from "@agir/front/genericComponents/images/group_financement.svg";
import group_general from "@agir/front/genericComponents/images/group_general.svg";

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
  },
  management: {
    id: "management",
    label: "Gestion et animation",
    icon: "lock",
    illustration: group_members,
    component: <GroupManagementPage />,
  },
  finance: {
    id: "finance",
    label: "Financement",
    icon: "sun",
    illustration: group_financement,
    component: <GroupFinancePage />,
  },
  general: {
    id: "general",
    label: "Général",
    icon: "file-text",
    illustration: group_general,
  },
  location: {
    id: "location",
    label: "Localisation",
    icon: "map-pin",
  },
  contact: {
    id: "contact",
    label: "Contact",
    icon: "mail",
  },
  links: {
    id: "links",
    label: "Liens et réseaux sociaux",
    icon: "at-sign",
  },
};

export const DEFAULT_GROUP = {
  title: "Cortège France insoumise à la marche contre la fourrure 2020",
  // membersCount: 3,
};
