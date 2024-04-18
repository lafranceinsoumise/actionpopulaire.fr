import { useCallback, useEffect, useMemo } from "react";

import { login } from "@agir/front/authentication/api";
import { routeConfig } from "@agir/front/app/routes.config";
import { useHistory, useLocation } from "react-router-dom";

const AutoLogin = ({ email }) => {
  const history = useHistory();
  const location = useLocation();

  const next = useMemo(() => {
    if (location.state?.next) {
      return location.state.next;
    }

    if (location.search) {
      return new URLSearchParams(location.search).get("next");
    }
  }, [location.state, location.search]);

  const autoLogin = useCallback(
    async (email) => {
      const result = await login(email);
      let redirectTo = result.error
        ? routeConfig.logout.getLink()
        : routeConfig.codeLogin.getLink();

      history.push(redirectTo, {
        ...(location.state || {}),
        next,
        email: email,
        code: result.data && result.data.code,
        auto: true,
      });
    },
    [next, history, location.state],
  );

  useEffect(() => {
    autoLogin(email);
  }, [email, autoLogin]);

  return null;
};

export default AutoLogin;
