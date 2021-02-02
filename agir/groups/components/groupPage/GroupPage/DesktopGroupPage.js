import PropTypes from "prop-types";
import React, { useCallback } from "react";
import { Switch, Route, useHistory } from "react-router-dom";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";
import { routeConfig } from "@agir/front/app/routes.config";
import { useTabs } from "./routes.config";

import { Column, Container, Row } from "@agir/front/genericComponents/grid";
import Link from "@agir/front/app/Link";
import Skeleton from "@agir/front/genericComponents/Skeleton";

import GroupBanner from "@agir/groups/groupPage/GroupBanner";
import GroupUserActions from "@agir/groups/groupPage/GroupUserActions";
import GroupContactCard from "@agir/groups/groupPage/GroupContactCard";
import GroupDescription from "@agir/groups/groupPage/GroupDescription";
import GroupLinks from "@agir/groups/groupPage/GroupLinks";
import GroupFacts from "@agir/groups/groupPage/GroupFacts";
import GroupDonation from "@agir/groups/groupPage/GroupDonation";
import GroupSuggestions from "@agir/groups/groupPage/GroupSuggestions";
import GroupPageMenu from "@agir/groups/groupPage/GroupPageMenu";
import GroupOrders from "@agir/groups/groupPage/GroupOrders";

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

const IndexLinkAnchor = styled(Link)`
  font-weight: 600;
  font-size: 12px;
  line-height: 1.4;
  text-transform: uppercase;
  display: flex;
  align-items: center;
  margin: 20px 0;
  &,
  &:hover,
  &:focus,
  &:active {
    text-decoration: none;
    color: #585858;
  }
  span {
    transform: rotate(180deg) translateY(-1.5px);
    transform-origin: center center;
  }
  @media (max-width: ${style.collapse}px) {
    padding: 0.5rem 1.375rem 0;
    margin-bottom: -1rem;
  }
`;

const DesktopGroupPage = (props) => {
  const { backLink, group, groupSuggestions, allEvents } = props;
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
      {!!backLink && (
        <Row gutter={32}>
          <Column grow>
            <IndexLinkAnchor
              to={backLink.to}
              href={backLink.href}
              route={backLink.route}
            >
              <span>&#10140;</span>
              &ensp; {backLink.label || "Retour à l'accueil"}
            </IndexLinkAnchor>
          </Column>
        </Row>
      )}
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
          <GroupOrders {...group} />
          {allEvents && allEvents.length > 0 ? (
            <GroupDescription {...group} />
          ) : null}
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
