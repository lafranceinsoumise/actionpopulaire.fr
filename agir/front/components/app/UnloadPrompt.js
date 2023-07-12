import PropTypes from "prop-types";
import React, { useCallback, useMemo } from "react";
import { Prompt } from "react-router-dom";
import { useBeforeUnload } from "react-use";

import { routeConfig } from "@agir/front/app/routes.config";

const DEFAULT_MESSAGE =
  "Cette page vous demande de confirmer sa fermeture; des données que vous avez saisies pourraient ne pas être enregistrées. Confirmez-vous vouloir quitter la page ?";

const UnloadPrompt = (props) => {
  const { enabled, message = DEFAULT_MESSAGE, allowedRoutes } = props;
  useBeforeUnload(enabled, message);
  const msg = useCallback(
    (location) => {
      if (!allowedRoutes) {
        return message;
      }
      return (
        allowedRoutes
          .split(",")
          .some(
            (route) =>
              routeConfig[route] && routeConfig[route].match(location.pathname),
          ) || message
      );
    },
    [allowedRoutes, message],
  );
  return <Prompt when={enabled} message={msg} />;
};
UnloadPrompt.propTypes = {
  enabled: PropTypes.bool,
  message: PropTypes.string,
  allowedRoutes: PropTypes.string,
};

export default UnloadPrompt;
