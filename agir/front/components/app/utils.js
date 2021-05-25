import React, { lazy as reactLazy, useEffect, useMemo, useState } from "react";
import { useIsOffline } from "@agir/front/allPages/NotFound/hooks";

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
              throw err;
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
      [lazyImport, error, fallback]
    );

    useEffect(() => {
      error && !isOffline && setError(null);
    }, [error, isOffline]);

    return <Lazy {...props} />;
  };

  LazyComponent.displayName = `LazyComponent`;
  LazyComponent.preload = lazyImport;

  return LazyComponent;
};
