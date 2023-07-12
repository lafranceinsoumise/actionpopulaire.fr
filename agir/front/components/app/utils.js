import React, { lazy as reactLazy, useEffect, useMemo, useState } from "react";
import { useHistory } from "react-router-dom";
import { useIsOffline } from "@agir/front/offline/hooks";
import { getScrollableParent } from "@agir/lib/utils/dom";

export const lazy = (lazyImport, fallback) => {
  const LazyComponent = (props) => {
    const isOffline = useIsOffline();
    const [error, setError] = useState(null);

    const Lazy = useMemo(
      () =>
        reactLazy(async () => {
          try {
            return await lazyImport();
          } catch (err) {
            if (err.name !== "ChunkLoadError") {
              if (err instanceof Error) {
                throw err;
              }
              const message = err?.message
                ? err.message
                : typeof err === "string"
                ? err
                : "Lazy loading failed.";
              throw new Error(message);
            }
            setError(err.toString());
            const Fallback = () =>
              typeof fallback !== "undefined" ? (
                fallback
              ) : (
                <div>
                  <h2>Erreur</h2>
                  <p>
                    {process.env.NODE_ENV === "production"
                      ? "Nous n'avons pas pu charger cette page."
                      : err.toString()}
                  </p>
                </div>
              );
            return {
              default: Fallback,
            };
          }
        }),
      //eslint-disable-next-line
      [lazyImport, error, fallback],
    );

    useEffect(() => {
      error && !isOffline && setError(null);
    }, [error, isOffline]);

    return <Lazy {...props} />;
  };

  LazyComponent.displayName = `LazyComponent`;
  LazyComponent.preload = async () => {
    try {
      return await lazyImport();
    } catch (err) {
      if (err.name !== "ChunkLoadError" && err instanceof Error) {
        throw err;
      }
    }
  };

  return LazyComponent;
};

export const scrollToError = (errors, scrollerElement, marginTop = 30) => {
  if (!errors) {
    return;
  }

  if (!scrollerElement || !Object.values(errors).some(Boolean)) {
    return;
  }

  const keys = Object.entries(errors)
    .filter(([_, v]) => !!v)
    .map(([k]) => k);

  const scrollableElement = getScrollableParent(scrollerElement);

  let errorElement = null;
  for (let i = 0; i < keys.length; i += 1) {
    let elt = document.querySelector(
      `[data-scroll="${keys[i]}"], [name="${keys[i]}"]`,
    );
    if (!elt) {
      continue;
    }
    if (!errorElement) {
      errorElement = elt;
      continue;
    }
    if (elt.offsetTop < errorElement.offsetTop) {
      errorElement = elt;
    }
  }
  errorElement &&
    scrollableElement &&
    scrollableElement.scrollTo({
      top: errorElement.offsetTop - marginTop,
    });
};

export const useCurrentLocation = () => {
  const [pathname, setPathname] = useState(window.location.pathname);
  const history = useHistory();

  useEffect(() => {
    history?.listen((location) => {
      setPathname(location.pathname);
    }) || setPathname(window.location.pathname);
  }, [history]);

  return pathname;
};
