import PropTypes from "prop-types";
import React, { useCallback, useEffect, useMemo, useRef } from "react";
import { Switch, Route, useHistory } from "react-router-dom";
import { useSpring, animated } from "react-spring";
import { useDrag } from "react-use-gesture";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

import { routeConfig } from "@agir/front/app/routes.config";
import { useTabs } from "./routes.config";

import { Column, Container, Row } from "@agir/front/genericComponents/grid";
import Skeleton from "@agir/front/genericComponents/Skeleton";

import GroupBanner from "../GroupBanner";

import GroupUserActions from "../GroupUserActions";
import GroupPageMenu from "../GroupPageMenu";

import Routes from "./Routes";

export const MobileGroupPageSkeleton = () => (
  <Container style={{ margin: "2rem auto", padding: "0 1rem" }}>
    <Row>
      <Column stack>
        <Skeleton />
      </Column>
    </Row>
  </Container>
);

const StyledTab = styled(animated.div)`
  max-width: 100%;
  margin: 0;
  padding: 0;
  scroll-margin-top: 160px;

  @media (max-width: ${style.collapse}px) {
    scroll-margin-top: 120px;
    min-height: 100vh;
  }
`;

// TODO: fix swiping behavior
const SwipeableTab = (props) => {
  const { onNextTab, onPrevTab, children } = props;
  const [{ xy }, set] = useSpring(() => ({ xy: [0, 0] }));
  const bind = useDrag(
    ({ args: [limit], down, movement: [x] }) => {
      if (down) {
        const newX =
          x > 0 ? Math.min(Math.abs(limit), x) : Math.max(-Math.abs(limit), x);
        set({ xy: [newX, 0] });
        return;
      }
      set({ xy: [0, 0] });
      if (Math.abs(x) > Math.abs(limit)) {
        x <= 0 ? onNextTab && onNextTab() : onPrevTab && onPrevTab();
      }
    },
    { axis: "x", lockDirection: true }
  );
  const tabRef = useRef();

  useEffect(() => {
    tabRef.current & tabRef.current.scrollIntoView();
  }, []);

  return (
    <StyledTab
      {...bind(50)}
      style={{
        transform:
          xy && xy.interpolate((x) => (x ? `translate3d(${x}px, 0px, 0)` : "")),
      }}
      ref={tabRef}
    >
      {children}
    </StyledTab>
  );
};
SwipeableTab.propTypes = {
  onNextTab: PropTypes.func,
  onPrevTab: PropTypes.func,
  children: PropTypes.node,
};

const Tab = (props) => {
  const { children } = props;
  const tabRef = useRef();
  useEffect(() => {
    tabRef.current & tabRef.current.scrollIntoView();
  }, []);

  return <StyledTab ref={tabRef}>{children}</StyledTab>;
};
Tab.propTypes = {
  onNextTab: PropTypes.func,
  onPrevTab: PropTypes.func,
  children: PropTypes.node,
};

const MobileGroupPage = (props) => {
  const { group, allEvents } = props;
  const { hasTabs, tabs, onTabChange, onNextTab, onPrevTab } = useTabs(
    props,
    true
  );

  const goToAgendaTab = useMemo(() => {
    const agendaTab = tabs.find((tab) => tab.id === "agenda");
    if (agendaTab && onTabChange) {
      return () => onTabChange(agendaTab);
    }
  }, [tabs, onTabChange]);

  const history = useHistory();

  const getMessageURL = useCallback(
    (messagePk) =>
      routeConfig.groupMessage &&
      routeConfig.groupMessage.getLink({
        groupPk: group.id,
        messagePk: messagePk,
      }),
    [group]
  );

  const handleClickMessage = useCallback(
    (message) => {
      const link = getMessageURL(message.id);
      history && history.push(link);
    },
    [history, getMessageURL]
  );

  if (!group) {
    return null;
  }

  return (
    <Container
      style={{
        margin: 0,
        padding: "0 0 3.5rem",
        backgroundColor: style.black25,
      }}
    >
      <GroupBanner {...group} />
      <GroupUserActions {...group} />
      <GroupPageMenu tabs={tabs} hasTabs={hasTabs} stickyOffset={72} />
      <Switch>
        {tabs.map((tab) => {
          const R = Routes[tab.id];
          return (
            <Route key={tab.id} path={tab.pathname} exact>
              <Tab onNextTab={onNextTab} onPrevTab={onPrevTab}>
                <R
                  {...props}
                  allEvents={allEvents}
                  hasTabs={hasTabs}
                  goToAgendaTab={goToAgendaTab}
                  getMessageURL={getMessageURL}
                  onClickMessage={handleClickMessage}
                />
              </Tab>
            </Route>
          );
        })}
      </Switch>
    </Container>
  );
};
MobileGroupPage.propTypes = {
  group: PropTypes.object,
  allEvents: PropTypes.arrayOf(PropTypes.object),
};
export default MobileGroupPage;
