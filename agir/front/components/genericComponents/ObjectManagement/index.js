import PropTypes from "prop-types";
import React, { useCallback } from "react";
import { Route, useHistory, useRouteMatch } from "react-router-dom";

import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

import { useIsDesktop } from "@agir/front/genericComponents/grid";
import Panel from "@agir/front/genericComponents/Panel";
import ManagementMenu from "@agir/front/genericComponents/ObjectManagement/ManagementMenu";
import ManagementPanel from "@agir/front/genericComponents/ObjectManagement/ManagementPanel";

const StyledPanel = styled(Panel)`
  padding: 0;
  display: flex;
  flex-flow: row nowrap;
  min-width: 0;

  @media (max-width: ${style.collapse}px) {
    min-width: 100%;
    width: 100%;
  }
`;

export const ObjectManagement = (props) => {
  const { title, object, basePath, routes, menuRoute, ...rest } = props;

  const isDesktop = useIsDesktop();
  const history = useHistory();

  const hasRoute = useRouteMatch(menuRoute.getLink());

  const goToMenu = useCallback(() => {
    history.push(menuRoute.getLink());
  }, [menuRoute, history]);

  const closePanel = useCallback(() => {
    history.push(basePath);
  }, [basePath, history]);

  return (
    <StyledPanel
      shouldShow={!!hasRoute}
      position="left"
      noScroll
      onClose={closePanel}
    >
      <Route key={menuRoute.id} path={menuRoute.getLink()} exact={!isDesktop}>
        <ManagementMenu
          title={title}
          object={object}
          items={routes}
          onBack={closePanel}
        />
      </Route>
      {routes.map((route) => (
        <Route key={route.id} path={route.getLink()} exact={route.exact}>
          <ManagementPanel showPanel>
            <route.Component
              {...rest}
              illustration={route.illustration}
              onBack={goToMenu}
            />
          </ManagementPanel>
        </Route>
      ))}
    </StyledPanel>
  );
};
ObjectManagement.propTypes = {
  title: PropTypes.string,
  object: PropTypes.object,
  basePath: PropTypes.string.isRequired,
  routes: PropTypes.arrayOf(PropTypes.object).isRequired,
  menuRoute: PropTypes.object.isRequired,
};

export default ObjectManagement;
