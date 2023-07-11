import { useMemo } from "react";
import { getGenderedWord } from "@agir/lib/utils/display";

export const MEMBERSHIP_TYPES = {
  FOLLOWER: 5,
  MEMBER: 10,
  MANAGER: 50,
  REFERENT: 100,
};

export const MEMBERSHIP_TYPE_ICON = {
  [MEMBERSHIP_TYPES.FOLLOWER]: "rss",
  [MEMBERSHIP_TYPES.MEMBER]: "user",
  [MEMBERSHIP_TYPES.MANAGER]: "settings",
  [MEMBERSHIP_TYPES.REFERENT]: "lock",
};

export const MEMBERSHIP_TYPE_LABEL = {
  [MEMBERSHIP_TYPES.FOLLOWER]: "Contact du groupe",
  [MEMBERSHIP_TYPES.MEMBER]: "Membre actif",
  [MEMBERSHIP_TYPES.MANAGER]: "Gestionnaire",
  [MEMBERSHIP_TYPES.REFERENT]: ["Animateur·ice", "Animatrice", "Animateur"],
};

const LFI_NSP_GROUP_WORD_LABELS = {
  "votre groupe doit être animé": "votre équipe doit être animée",
  "un autre groupe": "une autre équipe",
  "du groupe": "de l'équipe",
  "au groupe": "à l'équipe",
  "des groupes": "des équipes",
  "aux groupes": "aux équipes",
  "de groupe": "d'équipe",
  "le groupe": "l'équipe",
  "un groupe": "une équipe",
  "d'actions": "de soutien",
  groupes: "équipes",
  groupe: "équipe",
};

export const withGroupWord =
  (is2022) =>
  (strings, ...params) => {
    let sentence = strings
      .map((s, i) => (params[i] ? s + params[i] : s))
      .join("");
    Object.entries(LFI_NSP_GROUP_WORD_LABELS).forEach(([lfi, nsp]) => {
      sentence = is2022
        ? sentence.replace(lfi, nsp)
        : sentence.replace(nsp, lfi);
    });
    return sentence;
  };

export const useGroupWord = (group) => {
  const is2022 = useMemo(() => !!group?.is2022, [group]);
  const templateTag = useMemo(() => withGroupWord(is2022), [is2022]);

  return templateTag;
};

export const getGenderedMembershipType = (membershipType, gender) => {
  const label = MEMBERSHIP_TYPE_LABEL[String(membershipType)];
  if (!label) {
    return "";
  }
  if (Array.isArray(label)) {
    return getGenderedWord(gender, ...label);
  }
  return label;
};
