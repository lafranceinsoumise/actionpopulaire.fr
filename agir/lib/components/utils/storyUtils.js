import { DateTime, Duration, Interval } from "luxon";
import pipe from "lodash/fp/flow";
import get from "lodash/fp/get";
import set from "lodash/fp/set";
import has from "lodash/fp/has";
import unset from "lodash/fp/unset";

/**
 * Permet de prétraiter des arguments pour un composant React dans une story
 *
 * Cette fonction prend un nombre variable d'arguments : le dernier est le composant
 * React, et les (n-1) premiers sont des fonctions qui prennent les arguments et
 * renvoient des arguments modifiés.
 *
 * Cela permet par exemple de convertir des valeurs au bon type, ou de regrouper des
 * valeurs qui avaient dû être aplaties pour l'Add-on controls dans un objet.
 *
 * Les différents décorateurs sont appliqués dans le sens spécifié.
 * @returns Un nouveau composant React
 */
export function decorateArgs() {
  const args = Array.from(arguments);
  const component = args[args.length - 1];
  const decorators = args.slice(0, -1);
  return (args) => component(pipe(decorators)(args));
}

/**
 * Ajoute l'argument `schedule` à partir des deux arguments `startTime` and `duration`
 *
 * `startTime` doit être en millisecondes depuis l'Epoch (format par défaut du composant Date de storybook.
 * `duration` doit être en nombre d'heures.
 *
 * L'attribut `schedule` ajouté est un `Interval` luxon.
 *
 * @param target: le sous-objet sur lequel se trouvent les arguments,
 * @returns La fonction de décoration des arguments à utiliser comme argument de decorateArgs
 */
export const scheduleFromStartTimeAndDuration = (target) => (args) => {
  const targetPrefix = target && target.length ? target + "." : "";
  const startTime = get(`${targetPrefix}startTime`, args);
  const duration = get(`${targetPrefix}duration`, args);

  return pipe([
    unset(`${targetPrefix}startTime`),
    unset(`${targetPrefix}duration`),
    set(
      `${targetPrefix}schedule`,
      Interval.after(
        DateTime.fromMillis(+startTime, {
          zone: "Europe/Paris",
          locale: "fr",
        }),
        Duration.fromObject({ hours: duration }),
      ),
    ),
  ])(args);
};

/**
 * Permet de renommer/réorganiser les arguments.
 *
 * L'argument `combinations` est un objet javascript décrivant les renommages et déplacements à effectuer.
 * Chaque clé est un attribut à modifier/créer.
 *
 * @param combinations: l'objet javascript décrivant les transformations à effectuer
 * @param replace: s'il faut remplacer les attributs existant, ou merger les valeurs (superficiellement)
 * @returns le paramètre args enrichi
 *
 * Exemples :
 * - Ajoute un argument `newStatus`, de valeur égale à l'argument `status`.
 *   `reorganize({newStatus: "status"})`
 *
 * - Ajouter un argument location, un objet javascript, avec deux clés `name` et  `address`
 *   de valeurs respectivement égales aux arguments `locationName` et `locationAddress`.
 *   `reorganize({location: {name: "locationName", address: "locationAddress"}})`
 *
 */
export const reorganize =
  (combinations, replace = true) =>
  (args) => {
    for (let attr of Object.keys(combinations)) {
      const value = getValue(args, combinations[attr]);
      if (!replace && has(attr, args)) {
        args = set(attr, { ...get(attr, args), ...value }, args);
      } else {
        args = set(attr, value, args);
      }
    }
    return args;
  };

const getValue = (args, value) => {
  if (typeof value === "string") {
    return get(value, args);
  } else {
    return Object.keys(value).reduce(
      (result, key) => ({
        ...result,
        [key]: getValue(args, value[key]),
      }),
      {},
    );
  }
};
