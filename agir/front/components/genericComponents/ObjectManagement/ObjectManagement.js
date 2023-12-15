import PropTypes from "prop-types";
import React, { Suspense, useCallback, useEffect, useRef } from "react";
import {
  Switch,
  Redirect,
  Route,
  useHistory,
  useLocation,
  useRouteMatch,
} from "react-router-dom";
import { animated, useTransition } from "@react-spring/web";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

import { ResponsiveLayout } from "@agir/front/genericComponents/grid";
import Panel from "@agir/front/genericComponents/Panel";
import ManagementMenu from "@agir/front/genericComponents/ObjectManagement/ManagementMenu";
import ManagementPanel from "@agir/front/genericComponents/ObjectManagement/ManagementPanel";

const StyledSubPanel = styled(animated.div)`
  box-shadow: ${style.elaborateShadow};
  width: 100%;
  height: 100%;
  will-change: transform, opacity;
  position: absolute;
  top: 0;
  left: 0;

  &:empty {
    display: none;
  }

  @media (min-width: ${style.collapse}px) {
    display: flex;
    & > * {
      flex: 0 0 auto;
    }
  }
`;

const StyledPanel = styled(Panel)`
  && {
    padding: 0;
    overflow-x: hidden;
    background-color: transparent;

    @media (min-width: ${style.collapse}px) {
      min-width: 0;
      display: flex;
      flex-flow: row nowrap;

      & > * {
        flex: 1 1 auto;

        &:first-child {
          z-index: 2;
        }
      }
    }
  }
`;

const slideInTransition = {
  mobile: {
    keys: ({ pathname }) => pathname,
    from: { transform: "translateX(66%)" },
    enter: { transform: "translateX(0%)" },
    leave: { transform: "translateX(100%)" },
  },
  desktop: {
    keys: ({ pathname }) => pathname,
    from: { transform: "translateX(-66%)", opacity: 1 },
    enter: { transform: "translateX(0%)", opacity: 1 },
    leave: { transform: "translateX(0%)", opacity: 0.8 },
  },
};

const MobilePanel = (props) => {
  const {
    title,
    subtitle,
    routes,
    menuLink,
    shouldShow,
    onClose,
    goToMenu,
    ...rest
  } = props;

  const location = useLocation();
  const shouldAnimate = useRef(shouldShow ? 1 : 0);

  useEffect(() => {
    shouldAnimate.current = shouldShow ? shouldAnimate.current + 1 : 0;
    // eslint-disable-next-line
  }, [location.pathname, shouldShow]);

  const transition = useTransition(location, slideInTransition.mobile);

  return (
    <StyledPanel shouldShow={shouldShow} onClose={onClose} noScroll>
      <ManagementMenu
        title={title}
        subtitle={subtitle}
        items={routes}
        onBack={onClose}
        {...rest}
      />
      {transition((style, item) => (
        <StyledSubPanel style={shouldAnimate.current > 1 ? style : undefined}>
          <Switch location={item}>
            {routes.map((route) => (
              <Route key={route.id} path={route.path} exact={route.exact}>
                <ManagementPanel>
                  <Suspense fallback={null}>
                    <route.Component
                      {...rest}
                      illustration={route.illustration}
                      onBack={goToMenu}
                    />
                  </Suspense>
                </ManagementPanel>
              </Route>
            ))}
            <Route key="unhandled-route" path={menuLink + "*"} exact>
              <Redirect to={menuLink} />
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
    subtitle,
    routes,
    menuLink,
    shouldShow,
    onClose,
    goToMenu,
    ...rest
  } = props;

  const location = useLocation();
  const transition = useTransition(location, slideInTransition.desktop);

  return (
    <StyledPanel
      shouldShow={shouldShow}
      position="left"
      noScroll
      onClose={onClose}
    >
      <ManagementMenu
        title={title}
        subtitle={subtitle}
        items={routes}
        onBack={onClose}
        {...rest}
      />
      <div
        style={{
          minWidth: "600px",
          height: "100%",
          position: "relative",
        }}
      >
        {transition((style, item) => (
          <StyledSubPanel style={style}>
            <Switch location={item}>
              {routes.map((route) => (
                <Route key={route.id} path={route.path} exact={route.exact}>
                  <ManagementPanel>
                    <Suspense fallback={null}>
                      <route.Component
                        {...rest}
                        illustration={route.illustration}
                        onBack={goToMenu}
                        route={route}
                      />
                    </Suspense>
                  </ManagementPanel>
                </Route>
              ))}
              <Route key="unhandled-route" path={menuLink + "*"} exact>
                <Redirect to={menuLink} />
              </Route>
            </Switch>
          </StyledSubPanel>
        ))}
      </div>
    </StyledPanel>
  );
};

MobilePanel.propTypes = DesktopPanel.propTypes = {
  title: PropTypes.string,
  subtitle: PropTypes.string,
  object: PropTypes.object,
  routes: PropTypes.arrayOf(PropTypes.object).isRequired,
  menuLink: PropTypes.string,
  shouldShow: PropTypes.bool,
  onClose: PropTypes.func,
  goToMenu: PropTypes.func,
};

export const ObjectManagement = (props) => {
  const { basePath, menuLink, redirectTo, ...rest } = props;

  const hasRoute = useRouteMatch(menuLink);

  const { push } = useHistory();

  const goToMenu = useCallback(() => {
    menuLink && push(menuLink);
  }, [menuLink, push]);

  const closePanel = useCallback(() => {
    basePath && push(basePath);
  }, [basePath, push]);

  if (!!hasRoute && redirectTo) {
    return <Redirect to={redirectTo} />;
  }

  return (
    <ResponsiveLayout
      {...rest}
      MobileLayout={MobilePanel}
      DesktopLayout={DesktopPanel}
      menuLink={menuLink}
      shouldShow={!!hasRoute}
      goToMenu={goToMenu}
      onClose={closePanel}
    />
  );
};
ObjectManagement.propTypes = {
  title: PropTypes.string,
  subtitle: PropTypes.string,
  basePath: PropTypes.string.isRequired,
  routes: PropTypes.arrayOf(PropTypes.object).isRequired,
  menuLink: PropTypes.string.isRequired,
  redirectTo: PropTypes.oneOfType([PropTypes.string, PropTypes.object]),
};

export default React.memo(ObjectManagement);
