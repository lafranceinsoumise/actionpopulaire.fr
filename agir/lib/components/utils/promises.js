import funcDebounce from "lodash/debounce";

export const debounce = (func, wait) => {
  let currentPromise = null;
  let currentResolve = null;
  let lastArgs;

  const debouncedResolve = funcDebounce(
    () => {
      currentResolve();
      currentResolve = null;
    },
    wait,
    { leading: false, trailing: true },
  );

  return (...args) => {
    if (currentResolve === null) {
      currentPromise = new Promise((resolve) => {
        currentResolve = resolve;
      }).then(() => func(...lastArgs));
    }
    lastArgs = args;

    debouncedResolve();
    return currentPromise;
  };
};
