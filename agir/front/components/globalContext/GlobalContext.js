import PropTypes from "prop-types";
import React, { useContext, useEffect, useMemo, Suspense } from "react";
import { StateInspector, useReducer } from "reinspect";
import { ThemeProvider } from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

import rootReducer from "@agir/front/globalContext/reducers";
import createDispatch, {
  initFromScriptTag,
  setSessionContext,
} from "@agir/front/globalContext/actions";
import useSWR from "swr";

import logger from "@agir/lib/utils/logger";
import { lazy } from "@agir/front/app/utils";
const log = logger(__filename);

const Toasts = lazy(() => import("@agir/front/globalContext/Toast"), null);

const GlobalContext = React.createContext({});

const ProdProvider = ({ hasRouter = false, hasToasts = false, children }) => {
  const [state, dispatch] = useReducer(
    rootReducer,
    rootReducer({}, initFromScriptTag(hasRouter)),
    (state) => state,
    "GC"
  );

  const doDispatch = useMemo(() => createDispatch(dispatch), [dispatch]);

  const { data: sessionContext } = useSWR("/api/session/");

  useEffect(() => {
    if (!sessionContext) return;

    if (!sessionContext.user) {
      self.caches?.delete("session").catch((e) => {
        if (e.name !== "SecurityError") {
          throw e;
        }
      });
    }

    doDispatch(setSessionContext(sessionContext));
    log.debug("Update session context", sessionContext);
  }, [doDispatch, sessionContext]);

  return (
    <GlobalContext.Provider value={{ state, dispatch: doDispatch }}>
      <ThemeProvider theme={style}>
        {children}
        {hasToasts && state.toasts?.length > 0 ? (
          <Suspense fallback={null}>
            <Toasts />
          </Suspense>
        ) : null}
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
  hasRouter: PropTypes.bool,
};

export const GlobalContextProvider =
  process.env.NODE_ENV === "production" ? ProdProvider : DevProvider;

export const TestGlobalContextProvider = ({
  hasRouter = false,
  children,
  value,
}) => {
  const [state] = useReducer(rootReducer, rootReducer({}, initFromScriptTag()));
  const doDispatch = useMemo(() => () => {}, []);
  const currentState = useMemo(
    () => ({
      state: {
        hasRouter,
        ...state,
        ...value,
      },
      dispatch: doDispatch,
    }),
    [hasRouter, state, value, doDispatch]
  );

  return (
    <GlobalContext.Provider value={currentState}>
      {children}
    </GlobalContext.Provider>
  );
};
TestGlobalContextProvider.propTypes = {
  hasRouter: ProdProvider.bool,
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

export default GlobalContextProvider;
