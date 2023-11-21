import PropTypes from "prop-types";
import React, { useMemo } from "react";
import { useLocation, Redirect, useRouteMatch } from "react-router-dom";

import { useIsDesktop } from "@agir/front/genericComponents/grid";
import { routeConfig as globalRouteConfig } from "@agir/front/app/routes.config";
import { getMenuRoute, getRoutes } from "./routes.config";
import { useAuthentication } from "@agir/front/authentication/hooks";

import ObjectManagement from "@agir/front/genericComponents/ObjectManagement/ObjectManagement";

export const EventSettings = (props) => {
  const { event, basePath } = props;
  const routes = useMemo(() => getRoutes(basePath, event), [basePath, event]);
  const menuRoute = useMemo(() => getMenuRoute(basePath), [basePath]);
  const isAuthorized = useAuthentication(globalRouteConfig.eventSettings);
  const routeMenuMatch = useRouteMatch(menuRoute.path);
  const { pathname } = useLocation();
  const isDesktop = useIsDesktop();

  const redirectTo = useMemo(() => {
    if (!event?.isManager) {
      return basePath;
    }
    if (isAuthorized === false) {
      return {
        pathname: globalRouteConfig.login.getLink(),
        state: { next: pathname },
      };
    }
    return null;
  }, [event, isAuthorized, basePath, pathname]);

  if (!event) {
    return null;
  }

  // Open first panel on Desktop
  if (isDesktop && routeMenuMatch?.isExact) {
    return <Redirect to={routes[0] ? routes[0].getLink() : basePath} />;
  }

  const warning = !event.isEditable ? (
    <>
      Cet événement n'est pas modifiable directement via Action Populaire.
      <br />
      Pour toute question, veuillez contacter nos équipes à l'adresse e-mail{" "}
      <strong>groupes@actionpopulaire.fr</strong>
    </>
  ) : undefined;

  return (
    <ObjectManagement
      title={event?.name}
      warning={warning}
      eventPk={event?.id}
      basePath={basePath}
      routes={routes}
      menuLink={menuRoute.getLink()}
      redirectTo={redirectTo}
      isPast={event?.isPast}
    />
  );
};
EventSettings.propTypes = {
  event: PropTypes.shape({
    id: PropTypes.string,
    name: PropTypes.string,
    type: PropTypes.string,
    isOrganizer: PropTypes.bool,
    isPast: PropTypes.bool,
    endTime: PropTypes.string,
  }).isRequired,
  basePath: PropTypes.string.isRequired,
};

export default EventSettings;
