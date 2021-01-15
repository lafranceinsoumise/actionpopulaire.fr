import PropTypes from "prop-types";
import React, { useContext, useEffect, useMemo } from "react";
import { StateInspector, useReducer } from "reinspect";
import { ThemeProvider } from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

import rootReducer from "@agir/front/globalContext/reducers";
import createDispatch, {
  initFromScriptTag,
  setSessionContext,
} from "@agir/front/globalContext/actions";
import Toasts from "@agir/front/globalContext/Toast";
import useSWR from "swr";

import logger from "@agir/lib/utils/logger";
const log = logger(__filename);

const GlobalContext = React.createContext({});

const ProdProvider = ({ hasToasts = false, children }) => {
  const [state, dispatch] = useReducer(
    rootReducer,
    rootReducer({}, initFromScriptTag()),
    (state) => state,
    "GC"
  );

  const doDispatch = useMemo(() => createDispatch(dispatch), [dispatch]);

  const { data: sessionContext } = useSWR("/api/session/");

  useEffect(() => {
    if (!sessionContext) return;

    doDispatch(setSessionContext(sessionContext));
    log.debug("Update session context", sessionContext);
  }, [doDispatch, sessionContext]);

  return (
    <GlobalContext.Provider value={{ state, dispatch: doDispatch }}>
      <ThemeProvider theme={style}>
        {children}
        {hasToasts ? <Toasts /> : null}
      </ThemeProvider>
    </GlobalContext.Provider>
  );
};
const DevProvider = (props) => {
  return (
    <StateInspector name="actionpopulaire">
      <ProdProvider {...props} />
    </StateInspector>
  );
};
DevProvider.propTypes = ProdProvider.propTypes = {
  children: PropTypes.element,
  hasToasts: PropTypes.bool,
};

export const GlobalContextProvider =
  process.env.NODE_ENV === "production" ? ProdProvider : DevProvider;

export const TestGlobalContextProvider = ({ children, value }) => {
  const [state] = useReducer(rootReducer, rootReducer({}, initFromScriptTag()));
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

export const useGlobalContext = () => useContext(GlobalContext);
export const useSelector = (selector) => {
  const { state } = useContext(GlobalContext);
  return selector(state);
};
export const useDispatch = () => {
  const { dispatch } = useContext(GlobalContext);
  return dispatch;
};
