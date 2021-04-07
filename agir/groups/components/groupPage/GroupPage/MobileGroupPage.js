import PropTypes from "prop-types";
import React, {
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";
import { Switch, Route, useHistory } from "react-router-dom";
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

const StyledTab = styled.div`
  max-width: 100%;
  margin: 0;
  padding: 0;
  scroll-margin-top: 160px;

  @media (max-width: ${style.collapse}px) {
    scroll-margin-top: 100px;
  }
`;

const Tab = (props) => {
  const { scrollIntoView, children } = props;
  const tabRef = useRef();
  useEffect(() => {
    scrollIntoView && tabRef.current && tabRef.current.scrollIntoView();
  }, [scrollIntoView]);
  return <StyledTab ref={tabRef}>{children}</StyledTab>;
};
Tab.propTypes = {
  scrollIntoView: PropTypes.bool,
  children: PropTypes.node,
};

const MobileGroupPage = (props) => {
  const { group, allEvents } = props;
  const { hasTabs, tabs, activeTabIndex, onTabChange } = useTabs(props, true);

  const goToAgendaTab = useMemo(() => {
    const agendaTab = tabs.find((tab) => tab.id === "agenda");
    if (agendaTab && onTabChange) {
      return () => onTabChange(agendaTab);
    }
  }, [tabs, onTabChange]);

  const goToMessagesTab = useMemo(() => {
    const messagesTab = tabs.find((tab) => tab.id === "messages");
    if (messagesTab && onTabChange) {
      return () => onTabChange(messagesTab);
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

  const [autoScroll, setAutoScroll] = useState(false);
  const navigationCount = useRef(0);
  useEffect(() => {
    navigationCount.current += 1;
    if (navigationCount.current > 1) {
      setAutoScroll(true);
    }
  }, [activeTabIndex]);

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
      <GroupPageMenu tabs={tabs} hasTabs={hasTabs} stickyOffset={56} />
      <Switch>
        {tabs.map((tab) => {
          const R = Routes[tab.id];
          return (
            <Route key={tab.id} path={tab.path} exact>
              <Tab scrollIntoView={hasTabs && autoScroll}>
                <R
                  {...props}
                  allEvents={allEvents}
                  hasTabs={hasTabs}
                  goToAgendaTab={goToAgendaTab}
                  goToMessagesTab={goToMessagesTab}
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
