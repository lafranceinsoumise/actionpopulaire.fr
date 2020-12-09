import React, { useContext, useMemo, useReducer } from "react";
import PropTypes from "prop-types";
import { ThemeProvider } from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

import rootReducer from "@agir/front/globalContext/reducers";
import createDispatch, { init } from "@agir/front/globalContext/actions";

const GlobalContext = React.createContext({});

export const GlobalContextProvider = ({ children }) => {
  const [state, dispatch] = useReducer(rootReducer, rootReducer({}, init()));
  const doDispatch = useMemo(() => createDispatch(dispatch), [dispatch]);

  return (
    <GlobalContext.Provider value={{ state, dispatch: doDispatch }}>
      <ThemeProvider theme={style}>{children}</ThemeProvider>
    </GlobalContext.Provider>
  );
};
GlobalContextProvider.propTypes = {
  children: PropTypes.element,
};

export const useGlobalContext = () => useContext(GlobalContext);

export const useSelector = (selector) => {
  const { state } = useContext(GlobalContext);
  return selector(state);
};

export const useDispatch = () => {
  const { dispatch } = useContext(GlobalContext);
  return dispatch;
};

export const TestGlobalContextProvider = ({ children, value }) => {
  const [state] = useReducer(rootReducer, rootReducer({}, init()));
  const doDispatch = useMemo(() => () => {}, []);
  const currentState = useMemo(
    () => ({
      state: {
        ...state,
        ...value,
      },
      dispatch: doDispatch,
    }),
    [state, value, doDispatch]
  );

  return (
    <GlobalContext.Provider value={currentState}>
      {children}
    </GlobalContext.Provider>
  );
};
TestGlobalContextProvider.propTypes = {
  children: PropTypes.node,
  value: PropTypes.object,
};
