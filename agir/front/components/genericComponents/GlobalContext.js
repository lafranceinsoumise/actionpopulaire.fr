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
  is2022: false,
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
  let newState = state;
  if (action.type === "@@INIT" && Array.isArray(action.activities)) {
    const { required } = parseActivities(action.activities);
    newState = {
      ...newState,
      requiredActionActivities: required,
    };
  }
  if (action.type === "@@INIT" && action.user && action.user.is2022) {
    newState = {
      ...newState,
      is2022: true,
    };
  }
  if (action.type === "setIs2022") {
    newState = {
      ...newState,
      is2022: true,
    };
  }
  if (
    action.type === "update-required-action-activities" &&
    Array.isArray(action.requiredActionActivities)
  ) {
    newState = {
      ...newState,
      requiredActionActivities: action.requiredActionActivities,
    };
  }
  return newState;
};

export const GlobalContextProvider = ({ children }) => {
  const globalContextScript = document.getElementById("globalContext");
  const extraContextScript = document.getElementById("extraContext");

  let globalContextData = defaultGlobalContextState;
  if (globalContextScript) {
    globalContextData = {
      ...globalContextData,
      ...JSON.parse(globalContextScript.textContent),
    };
  }
  if (extraContextScript) {
    globalContextData = {
      ...globalContextData,
      ...JSON.parse(extraContextScript.textContent),
    };
  }

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
