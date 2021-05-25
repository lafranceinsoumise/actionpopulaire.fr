import { useMemo } from "react";

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
