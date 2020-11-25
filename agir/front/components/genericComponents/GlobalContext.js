import React, { useEffect, useReducer } from "react";
import PropTypes from "prop-types";
import { ThemeProvider } from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

import { parseActivities } from "@agir/activity/common/helpers";

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
    const { required } = parseActivities(action.activities);
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
  const globalContextData = globalContextScript
    ? {
        ...defaultGlobalContextState,
        ...JSON.parse(globalContextScript.textContent),
      }
    : defaultGlobalContextState;

  const [state, dispatch] = useReducer(updateGlobalContext, globalContextData);

  useEffect(() => {
    dispatch({ type: "@@INIT", ...globalContextData });
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

export const TestGlobalContextProvider = ({ children, value }) => {
  const globalContextData = value
    ? {
        ...defaultGlobalContextState,
        ...value,
      }
    : defaultGlobalContextState;

  return (
    <GlobalContext.Provider value={globalContextData}>
      {children}
    </GlobalContext.Provider>
  );
};
TestGlobalContextProvider.propTypes = {
  children: PropTypes.node,
  value: PropTypes.object,
};
