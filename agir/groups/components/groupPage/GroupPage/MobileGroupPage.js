import PropTypes from "prop-types";
import React, { useCallback, useEffect, useMemo, useRef } from "react";
import { useHistory } from "react-router-dom";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

import { routeConfig } from "@agir/front/app/routes.config";
import { useTabs } from "./routes.config";
import { getGroupSettingLinks } from "@agir/groups/groupPage/GroupSettings/routes.config";

import { Column, Container, Row } from "@agir/front/genericComponents/grid";
import Skeleton from "@agir/front/genericComponents/Skeleton";

import GroupSettings from "@agir/groups/groupPage/GroupSettings";
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
  const { hasTabs, tabs, activeTabId, activePathname, onTabChange } = useTabs(
    props,
    true
  );

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

  const groupSettingsLinks = useMemo(
    () => (group?.id ? getGroupSettingLinks(group, activePathname) : null),
    [group, activePathname]
  );

  if (!group) {
    return null;
  }

  const R = Routes[activeTabId];

  return (
    <>
      <Container
        style={{
          margin: 0,
          padding: "0 0 3.5rem",
          backgroundColor: style.black25,
        }}
      >
        <GroupBanner {...group} groupSettingsLinks={groupSettingsLinks} />
        <GroupUserActions {...group} groupSettingsLinks={groupSettingsLinks} />
        <GroupPageMenu
          tabs={tabs}
          hasTabs={hasTabs}
          stickyOffset={56}
          activeTabId={activeTabId}
        />
        <Tab>
          <R
            {...props}
            groupSettingsLinks={groupSettingsLinks}
            allEvents={allEvents}
            hasTabs={hasTabs}
            goToAgendaTab={goToAgendaTab}
            goToMessagesTab={goToMessagesTab}
            getMessageURL={getMessageURL}
            onClickMessage={handleClickMessage}
          />
        </Tab>
      </Container>
      <GroupSettings group={group} basePath={activePathname} />
    </>
  );
};
MobileGroupPage.propTypes = {
  group: PropTypes.object,
  allEvents: PropTypes.arrayOf(PropTypes.object),
};
export default MobileGroupPage;
