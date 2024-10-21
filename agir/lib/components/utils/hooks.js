import { disableBodyScroll, clearAllBodyScrollLocks } from "body-scroll-lock";
import throttle from "lodash/throttle";
import debounce from "lodash/debounce";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useIntersection, useUpdateEffect } from "react-use";
import ResizeObserver from "resize-observer-polyfill";

import logger from "@agir/lib/utils/logger";

const log = logger(__filename);

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
    [wait],
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
 * @param {Array} deps éventuels paramètres supplémentaires dont le changement déclenche le "reset" du debounce.
 */
export const useDebounce = (func, wait, deps = []) => {
  const ref = useRef(null);
  ref.current = func;

  /* L'utilisation d'une fonction arrow pour appeler ref.current, plutôt
  que d'utiliser ref.current directe est délibérée ! Elle permet de s'assurer
  que c'est la valeur actuelle de la référence qui est utilisée à chaque fois
  que la fonction debounce s'active, alors qu'en indiquant directement ref.current,
  ç'aurait été la version au moment de la production du callback qui aurait été
  utilisée.

  exhaustive-deps n'arrive pas à identifier les dépendances et est désactivé ici. */
  // eslint-disable-next-line react-hooks/exhaustive-deps
  return useCallback(
    debounce((...args) => ref.current(...args), wait, {
      leading: false,
      trailing: true,
    }),
    [wait, ...deps],
  );
};

/**
 * Permet de mettre en place l'exécution d'un callback tous les `delay` secondes
 *
 * @param {Function} callback le callback à appeler régulièrement
 * @param {number} delay le nombre de millisecondes d'attente entre deux invocation du callback
 *
 * En cas de changement du delay, l'intervalle actuel est supprimé et un nouvel intervalle est créé.
 * Par exemple, si on était à 10 ms de la prochaine exécution, même si on réduit la longueur de l'intervalle
 * de 1000 à 500, la prochaine exécution aura lieu dans 500 ms (et non dans 10).
 */
export const useInterval = function useInterval(callback, delay) {
  const savedCallback = useRef();

  // Remember the latest callback.
  useEffect(() => {
    savedCallback.current = callback;
  }, [callback]);

  // Set up the interval.
  useEffect(() => {
    function tick() {
      savedCallback.current();
    }

    if (delay !== null) {
      let id = setInterval(tick, delay);
      return () => clearInterval(id);
    }
  }, [delay]);
};

export const useDisableBodyScroll = (isActive, shouldDisable) => {
  const targetRef = useRef(null);

  useEffect(() => {
    if (isActive && targetRef.current) {
      shouldDisable
        ? disableBodyScroll(targetRef.current, {
            allowTouchMove: () => true,
          })
        : clearAllBodyScrollLocks();
    }
    return () => {
      clearAllBodyScrollLocks();
    };
  }, [shouldDisable, isActive]);

  return targetRef;
};

export function useMeasure() {
  const ref = useRef();
  const [bounds, set] = useState({ left: 0, top: 0, width: 0, height: 0 });

  const [resizeObserver] = useState(
    () => new ResizeObserver(([entry]) => set(entry.contentRect)),
  );

  useEffect(() => {
    if (!resizeObserver) {
      return;
    }
    if (ref.current) {
      resizeObserver.observe(ref.current);
    }
    return () => resizeObserver.disconnect();
  }, [resizeObserver]);

  return [{ ref }, bounds];
}

export const useLocalStorage = (key, initialValue) => {

  const getCurrentValue = useCallback(() => {
    const item = window.localStorage.getItem(key);
    return item ? JSON.parse(item) : initialValue;
  }, [key])

  const [storedValue, setStoredValue] = useState(() => {
    try {
      return getCurrentValue()
    } catch (error) {
      log.debug(error);
      return initialValue;
    }
  });

  const refresh = useCallback(() => {
    setStoredValue(getCurrentValue())
  }, [key]);

  const update = useCallback((value) => {
    try {
      setStoredValue(value);
      window.localStorage.setItem(key, JSON.stringify(value));
    } catch (error) {
      log.debug(error);
    }
  }, []);

  const remove = useCallback(() => {
    try {
      setStoredValue(undefined);
      window.localStorage.clearItem(key);
    } catch (error) {
      log.debug(error);
    }
  }, []);

  return [storedValue, update, remove, refresh];
};

/**
 * Custom hook to implement an infinite scroll via an IntersectionObserver
 * @param  {function}  loadMore      a function to load more items or a falsy value to stop the infinite scroll
 * @param  {Boolean} isLoadingMore a boolean indicating if more items are being loaded
 * @return {function}                a React ref to use on the last item node of a list - once the node is on screen the loadMore function will
 *                                   be called unless isLoadingMore is true
 */
export const useInfiniteScroll = (loadMore, isLoadingMore) => {
  const intersectionRef = useRef(null);
  const intersection = useIntersection(intersectionRef, {
    root: null,
    rootMargin: "0px",
    threshold: 1,
  });

  useEffect(() => {
    !isLoadingMore && loadMore && intersection?.isIntersecting && loadMore();
  }, [intersection, isLoadingMore, loadMore]);

  return intersectionRef;
};

/**
 * Custom React hook to preload an image file and use its loading state
 * @param  {string} src  The image file URL
 * @return {boolean}     Whether the image file has been downloaded yet or not
 */
export const useImageLoad = (src) => {
  const [isLoaded, setIsLoaded] = useState(false);

  useEffect(() => {
    setIsLoaded(false);
    const onReady = () => {
      setIsLoaded(true);
    };
    const placeholder = new Image();
    placeholder.addEventListener("load", onReady);
    placeholder.addEventListener("error", onReady);
    placeholder.src = src;

    return () => {
      placeholder.removeEventListener("load", onReady);
      placeholder.removeEventListener("error", onReady);
    };
  }, [src]);

  return isLoaded;
};

export const getFocusableElements = (parent) => {
  if (!parent) {
    return [];
  }
  return [
    ...parent.querySelectorAll(
      'a[href], button, textarea, input[type="text"], input[type="radio"], input[type="checkbox"], select',
    ),
  ].filter(
    (elem) =>
      !elem.disabled &&
      !!(elem.offsetWidth || elem.offsetHeight || elem.getClientRects().length),
  );
};

export const useFocusTrap = (isTrapped) => {
  const targetElementRef = useRef(null);
  const handleTabKey = useCallback((e) => {
    if (!targetElementRef.current) {
      return;
    }
    const focusableModalElements = getFocusableElements(
      targetElementRef.current,
    );
    const firstElement = focusableModalElements[0];
    const lastElement =
      focusableModalElements[focusableModalElements.length - 1];
    if (!e.shiftKey && document.activeElement === lastElement) {
      firstElement.focus();
      e.preventDefault();
    }
    if (e.shiftKey && document.activeElement === firstElement) {
      lastElement.focus();
      e.preventDefault();
    }
  }, []);

  const keyListenersMap = useMemo(
    () => new Map([[9, handleTabKey]]),
    [handleTabKey],
  );

  useEffect(() => {
    const keyListener = (e) => {
      const listener = keyListenersMap.get(e.keyCode);
      return listener && listener(e);
    };
    if (isTrapped && targetElementRef.current) {
      document.addEventListener("keydown", keyListener);
      const firstElement = getFocusableElements(targetElementRef.current)[0];
      firstElement ? firstElement.focus() : targetElementRef.current.focus();
    }

    return () => document.removeEventListener("keydown", keyListener);
  }, [isTrapped, keyListenersMap]);

  return targetElementRef;
};

export const useResizeObserver = (ref, callback) => {
  const [width, setWidth] = useState();
  const [height, setHeight] = useState();

  const handleResize = useCallback(
    (entries) => {
      if (!Array.isArray(entries)) {
        return;
      }

      const entry = entries[0];
      const width = entry.contentRect.width;
      const height = entry.contentRect.height;

      setWidth(width);
      setHeight(height);

      if (callback) {
        callback(entry.contentRect);
      }
    },
    [callback],
  );

  useEffect(() => {
    if (!ref.current) {
      return;
    }

    let ROEntries = [];
    let RO = new ResizeObserver((entries) => {
      ROEntries = entries;
      window.requestAnimationFrame(() => handleResize(entries));
    });
    ref.current && RO.observe(ref.current);

    return () => {
      ROEntries.forEach((entry) => entry.target.remove());
      RO.disconnect();
    };
  }, [ref, handleResize]);

  return { width, height };
};
