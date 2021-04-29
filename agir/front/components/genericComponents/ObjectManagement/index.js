import PropTypes from "prop-types";
import React, { useCallback } from "react";
import {
  Switch,
  Redirect,
  Route,
  useHistory,
  useLocation,
  useRouteMatch,
} from "react-router-dom";

import { animated, useTransition } from "react-spring";

import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

import { ResponsiveLayout } from "@agir/front/genericComponents/grid";
import Panel from "@agir/front/genericComponents/Panel";
import ManagementMenu from "@agir/front/genericComponents/ObjectManagement/ManagementMenu";
import ManagementPanel from "@agir/front/genericComponents/ObjectManagement/ManagementPanel";

const StyledSubPanel = styled(animated.div)`
  @media (max-width: ${style.collapse}px) {
    width: 100%;
    height: 100%;
    position: absolute;
    box-shadow: ${style.elaborateShadow};
  }
`;

const StyledPanel = styled(Panel)`
  padding: 0;

  @media (min-width: ${style.collapse}px) {
    display: flex;
    flex-flow: row nowrap;
    min-width: 0;
  }
`;

const springConfig = {
  tension: 160,
  friction: 30,
};

const slideInTransition = {
  mobile: {
    config: springConfig,
    keys: (pathname) => pathname,
    immediate: true,
    from: { transform: "translateX(100%)" },
    enter: { transform: "translateX(0%)" },
    leave: { zIndex: -1 },
  },
  desktop: {
    config: springConfig,
    keys: (pathname) => pathname,
    trail: 100,
    order: ["leave", "enter", "update"],
    from: { zIndex: -1, transform: "translateX(-100%)" },
    enter: { zIndex: -1, transform: "translateX(0%)" },
    leave: { zIndex: -1, transform: "translateX(-100%)" },
  },
};

const MobilePanel = (props) => {
  const {
    title,
    routes,
    menuLink,
    shouldShow,
    onClose,
    goToMenu,
    ...rest
  } = props;

  const { pathname } = useLocation();
  const transition = useTransition(pathname, slideInTransition.mobile);

  return (
    <StyledPanel shouldShow={shouldShow} onClose={onClose} noScroll>
      {transition((style, item) => (
        <StyledSubPanel style={style}>
          <Switch location={{ pathname: item }}>
            {routes.map((route) => (
              <Route key={route.id} path={route.getLink()} exact>
                <ManagementPanel>
                  <route.Component
                    {...rest}
                    illustration={route.illustration}
                    onBack={goToMenu}
                  />
                </ManagementPanel>
              </Route>
            ))}
            <Route key="unhandled-route" path={menuLink + "*"} exact>
              <Redirect to={menuLink} />
            </Route>
            <Route key="menu" path={menuLink} exact>
              <ManagementMenu title={title} items={routes} onBack={onClose} />
            </Route>
          </Switch>
        </StyledSubPanel>
      ))}
    </StyledPanel>
  );
};

const DesktopPanel = (props) => {
  const {
    title,
    routes,
    menuLink,
    shouldShow,
    onClose,
    goToMenu,
    ...rest
  } = props;

  return (
    <StyledPanel
      shouldShow={shouldShow}
      position="left"
      noScroll
      onClose={onClose}
    >
      <ManagementMenu title={title} items={routes} onBack={onClose} />
      <StyledSubPanel style={style}>
        <Switch>
          {routes.map((route) => (
            <Route key={route.id} path={route.path} exact={route.exact}>
              <ManagementPanel>
                <route.Component
                  {...rest}
                  illustration={route.illustration}
                  onBack={goToMenu}
                />
              </ManagementPanel>
            </Route>
          ))}
          <Route key="unhandled-route" path={menuLink + "*"} exact>
            <Redirect to={menuLink} />
          </Route>
        </Switch>
      </StyledSubPanel>
    </StyledPanel>
  );
};

MobilePanel.propTypes = DesktopPanel.propTypes = {
  title: PropTypes.string,
  object: PropTypes.object,
  routes: PropTypes.arrayOf(PropTypes.object).isRequired,
  menuLink: PropTypes.string,
  shouldShow: PropTypes.bool,
  onClose: PropTypes.func,
  goToMenu: PropTypes.func,
};

export const ObjectManagement = (props) => {
  const { basePath, menuLink, ...rest } = props;

  const hasRoute = useRouteMatch(menuLink);
  const { push, replace } = useHistory();

  const goToMenu = useCallback(() => {
    menuLink && push(menuLink);
  }, [menuLink, push]);

  const closePanel = useCallback(() => {
    basePath && replace(basePath);
  }, [basePath, replace]);

  return (
    <ResponsiveLayout
      {...rest}
      MobileLayout={MobilePanel}
      DesktopLayout={DesktopPanel}
      shouldShow={!!hasRoute}
      goToMenu={goToMenu}
      onClose={closePanel}
    />
  );
};
ObjectManagement.propTypes = {
  title: PropTypes.string,
  basePath: PropTypes.string.isRequired,
  routes: PropTypes.arrayOf(PropTypes.object).isRequired,
  menuLink: PropTypes.string.isRequired,
};

export default React.memo(ObjectManagement);
