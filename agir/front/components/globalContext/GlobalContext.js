import PropTypes from "prop-types";
import React, { useContext, useEffect, useMemo, Suspense } from "react";
import { StateInspector, useReducer } from "reinspect";
import useSWR from "swr";

import style from "@agir/front/genericComponents/_variables.scss";

import QueryStringParamsActions from "./QueryStringParamsActions";
import ThemeProvider from "@agir/front/theme/ThemeProvider";

import rootReducer from "@agir/front/globalContext/reducers";
import createDispatch, {
  init,
  setSessionContext,
} from "@agir/front/globalContext/actions";

import logger from "@agir/lib/utils/logger";
import { lazy } from "@agir/front/app/utils";

const log = logger(__filename);

const Toasts = lazy(() => import("@agir/front/globalContext/Toast"), null);

const GlobalContext = React.createContext({});

const ProdProvider = ({ hasRouter = false, hasToasts = false, children }) => {
  const [state, dispatch] = useReducer(
    rootReducer,
    rootReducer({}, init(hasRouter)),
    (state) => state,
    "GC",
  );

  const doDispatch = useMemo(() => createDispatch(dispatch), [dispatch]);

  const { data: sessionContext } = useSWR("/api/session/");

  useEffect(() => {
    if (!sessionContext) return;

    if (!sessionContext.user) {
      self.caches?.delete("session").catch((err) => {
        if (err.name !== "SecurityError") {
          if (err instanceof Error) {
            throw err;
          }
          const message = err?.message
            ? err.message
            : typeof err === "string"
            ? err
            : "Session cache deletion failed.";
          throw new Error(message);
        }
      });
    }

    doDispatch(setSessionContext(sessionContext));
    log.debug("Update session context", sessionContext);
  }, [doDispatch, sessionContext]);

  return (
    <GlobalContext.Provider value={{ state, dispatch: doDispatch }}>
      <ThemeProvider>
        <QueryStringParamsActions user={sessionContext?.user} />
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
  children: PropTypes.node,
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
  const [state] = useReducer(rootReducer, rootReducer({}, init()));
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
    [hasRouter, state, value, doDispatch],
  );

  return (
    <GlobalContext.Provider value={currentState}>
      {children}
    </GlobalContext.Provider>
  );
};
TestGlobalContextProvider.propTypes = {
  hasRouter: PropTypes.bool,
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
