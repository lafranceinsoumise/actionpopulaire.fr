import { useRef, useEffect, useCallback } from "react";
import throttle from "lodash/throttle";
import debounce from "lodash/debounce";

export const usePrevious = (value) => {
  const ref = useRef(null);
  useEffect(() => {
    ref.current = value;
  }, [value]);

  return ref.current;
};

/**
 * Crée une version throttled de la fonction limite
 * Même si la fonction change, le throttling reste appliqué de
 * la même façon.
 *
 * Attention : changer la limite resette le throttling.
 *
 * @param {Function} func la fonction à throttler
 * @param {number} wait le nombre de millisecondes pour lesquelles throttler la fonction
 */
export const useThrottle = (func, wait) => {
  const ref = useRef(null);
  ref.current = func;

  /* exhaustive-deps n'arrive pas à identifier automatiquement les dépendances
     à cause de l'utilisation de la fonction externe throttle. On pourrait utiliser
     useMemo à la place mais l'objectif poursuivi serait moins clair. */

  // eslint-disable-next-line react-hooks/exhaustive-deps
  return useCallback(
    throttle((...args) => ref.current(...args), wait, {
      leading: true,
      trailing: true,
    }),
    [wait]
  );
};

/**
 * Crée une version debounced de la fonction limite
 * Même si la fonction change, le debounced reste appliqué de
 * la même façon.
 *
 * Attention : changer la limite resette le debounce.
 *
 * @param {Function} func la fonction à debouncer
 * @param {number} wait le nombre de millisecondes pour lesquelles debouncer la fonction
 */
export const useDebounce = (func, wait) => {
  const ref = useRef(null);
  ref.current = func;

  /* Idem, exhaustive-deps n'arrive pas à identifier les dépendances. */
  // eslint-disable-next-line react-hooks/exhaustive-deps
  return useCallback(
    debounce((...args) => ref.current(...args), wait, {
      leading: false,
      trailing: true,
    }),
    [wait]
  );
};
