import React, { useEffect, useReducer } from "react";
import PropTypes from "prop-types";
import { ThemeProvider } from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

import { parseActivities } from "@agir/activity/activityPage/ActivityList";

/*
 * Objet proxy utilisé en test pour toujours renvoyer quelque chose
 */
const routes = new Proxy(
  {},
  {
    get(_target, name) {
      return `#${name}`;
    },
  }
);

const defaultGlobalContextState = {
  activities: [],
  requiredActionActivities: [],
  user: null,
  domain: "https://agir.lafranceinsoumise.fr",
  csrfToken: null,
  routes,
};
const GlobalContext = React.createContext(defaultGlobalContextState);

// Example of a single reducer for the whole global context state
export const updateGlobalContext = (
  state = defaultGlobalContextState,
  action
) => {
  if (action.type === "@@INIT" && Array.isArray(action.activities)) {
    const [required] = parseActivities(action.activities);
    return {
      ...state,
      requiredActionActivities: required,
    };
  }
  if (
    action.type === "update-required-action-activities" &&
    Array.isArray(action.requiredActionActivities)
  ) {
    return {
      ...state,
      requiredActionActivities: action.requiredActionActivities,
    };
  }
  return state;
};

export const GlobalContextProvider = ({ children }) => {
  const globalContextScript = document.getElementById("globalContext");
  const globalContext = globalContextScript
    ? {
        ...globalContext,
        ...JSON.parse(globalContextScript.textContent),
      }
    : defaultGlobalContextState;

  const [state, dispatch] = useReducer(updateGlobalContext, globalContext);

  useEffect(() => {
    dispatch({ type: "@@INIT", ...globalContext });
    // eslint-disable-next-line
  }, []);

  return (
    <GlobalContext.Provider value={{ ...state, dispatch }}>
      <ThemeProvider theme={style}>{children}</ThemeProvider>
    </GlobalContext.Provider>
  );
};
GlobalContextProvider.propTypes = {
  children: PropTypes.element,
};

export const useGlobalContext = () => React.useContext(GlobalContext);

export const TestGlobalContextProvider = GlobalContext.Provider;
