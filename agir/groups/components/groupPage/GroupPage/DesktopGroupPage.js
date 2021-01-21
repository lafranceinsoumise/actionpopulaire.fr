import PropTypes from "prop-types";
import React, { useCallback } from "react";
import { Switch, Route, useHistory } from "react-router-dom";

import { routeConfig } from "@agir/front/app/routes.config";
import { useTabs } from "./routes.config";

import { Column, Container, Row } from "@agir/front/genericComponents/grid";
import Skeleton from "@agir/front/genericComponents/Skeleton";

import GroupBanner from "../GroupBanner";
import GroupUserActions from "../GroupUserActions";
import GroupContactCard from "../GroupContactCard";
import GroupDescription from "../GroupDescription";
import GroupLinks from "../GroupLinks";
import GroupFacts from "../GroupFacts";
import GroupDonation from "../GroupDonation";
import GroupSuggestions from "../GroupSuggestions";
import GroupPageMenu from "../GroupPageMenu";

import Routes from "./Routes";

export const DesktopGroupPageSkeleton = () => (
  <Container
    style={{
      margin: "4rem auto",
      padding: "2rem 0 4rem",
      background: "white",
    }}
  >
    <Row gutter={32} style={{ marginBottom: "3.5rem" }}>
      <Column grow>
        <Skeleton boxes={1} />
      </Column>
    </Row>
    <Row gutter={32}>
      <Column grow>
        <Skeleton />
      </Column>
      <Column width="460px">
        <Skeleton />
      </Column>
    </Row>
    <Row gutter={32}>
      <Column grow>
        <Skeleton boxes={1} />
      </Column>
    </Row>
  </Container>
);

const DesktopGroupPage = (props) => {
  const { group, groupSuggestions, allEvents } = props;
  const { hasTabs, tabs, activeTabIndex } = useTabs(props, false);
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
        margin: "4rem auto",
        padding: "0 4rem",
        background: "white",
      }}
    >
      <Row gutter={32}>
        <Column grow>
          <GroupBanner {...group} />
        </Column>
      </Row>

      <GroupPageMenu tabs={tabs} hasTabs={hasTabs} stickyOffset={72} />

      <Row
        gutter={32}
        style={{
          marginTop: "3.5rem",
          flexDirection: activeTabIndex === 0 ? "row" : "row-reverse",
        }}
      >
        <Switch>
          {tabs.map((tab) => {
            const R = Routes[tab.id];
            return (
              <Route key={tab.id} path={tab.pathname} exact>
                <Column grow>
                  <R
                    {...props}
                    allEvents={allEvents}
                    hasTabs={hasTabs}
                    onClickMessage={handleClickMessage}
                    getMessageURL={getMessageURL}
                    basePath={tab.getLink()}
                  />
                </Column>
              </Route>
            );
          })}
        </Switch>

        <Column width="460px">
          <GroupUserActions {...group} />
          <GroupContactCard {...group} />
          {allEvents.length > 0 ? <GroupDescription {...group} /> : null}
          <GroupLinks {...group} />
          <GroupFacts {...group} />
          {group.routes && group.routes.donations && (
            <GroupDonation url={group.routes.donations} />
          )}
        </Column>
      </Row>

      <Row gutter={32}>
        <Column grow>
          {Array.isArray(groupSuggestions) && groupSuggestions.length > 0 ? (
            <GroupSuggestions groups={groupSuggestions} />
          ) : null}
        </Column>
      </Row>
    </Container>
  );
};
DesktopGroupPage.propTypes = {
  backLink: PropTypes.object,
  group: PropTypes.shape({
    id: PropTypes.string,
    isMember: PropTypes.bool,
    isManager: PropTypes.bool,
    routes: PropTypes.shape({
      donations: PropTypes.string,
    }),
  }),
  groupSuggestions: PropTypes.arrayOf(PropTypes.object),
  upcomingEvents: PropTypes.arrayOf(PropTypes.object),
  pastEvents: PropTypes.arrayOf(PropTypes.object),
  allEvents: PropTypes.arrayOf(PropTypes.object),
};

export default DesktopGroupPage;
