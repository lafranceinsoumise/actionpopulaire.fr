import PropTypes from "prop-types";
import React, { useCallback, useMemo } from "react";
import { useHistory } from "react-router-dom";
import styled from "styled-components";

import { routeConfig } from "@agir/front/app/routes.config";
import { useTabs } from "./routes.config";

import { Column, Container, Row } from "@agir/front/genericComponents/grid";
import Skeleton from "@agir/front/genericComponents/Skeleton";

import GroupBanner from "@agir/groups/groupPage/GroupBanner";
import GroupContactCard from "@agir/groups/groupPage/GroupContactCard";
import GroupDescription from "@agir/groups/groupPage/GroupDescription";
import GroupDonation from "@agir/groups/groupPage/GroupDonation";
import GroupFacts from "@agir/groups/groupPage/GroupFacts";
import GroupLinks from "@agir/groups/groupPage/GroupLinks";
import GroupOrders from "@agir/groups/groupPage/GroupOrders";
import GroupPageMenu from "@agir/groups/groupPage/GroupPageMenu";
import GroupSuggestions from "@agir/groups/groupPage/GroupSuggestions";
import GroupUserActions from "@agir/groups/groupPage/GroupUserActions";

import GroupSettings from "@agir/groups/groupPage/GroupSettings/GroupSettings";
import { getGroupSettingLinks } from "@agir/groups/groupPage/GroupSettings/routes.config";

import BackLink from "@agir/front/app/Navigation/BackLink";
import Routes from "./Routes";

export const DesktopGroupPageSkeleton = () => (
  <Container
    css={`
      margin: 0 auto 4rem;
      padding: 0 4rem;
      background: ${(props) => props.theme.background0};
      max-width: 1336px;
      width: 100%;
    `}
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
      <Column width="320px">
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
  const { group, groupSuggestions, allEvents, backLink } = props;
  const { hasTabs, tabs, activeTabId, activePathname, onTabChange } = useTabs(
    props,
    false,
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
      routeConfig.messages.getLink({
        messagePk: messagePk,
      }),
    [],
  );

  const handleClickMessage = useCallback(
    (message) => {
      const link = getMessageURL(message.id);
      history && history.push(link);
    },
    [history, getMessageURL],
  );

  const groupSettingsLinks = useMemo(
    () => (group?.id ? getGroupSettingLinks(group, activePathname) : null),
    [group, activePathname],
  );

  if (!group) {
    return null;
  }

  const R = Routes[activeTabId];

  return (
    <>
      <Container
        css={`
          margin: 0 auto 4rem;
          padding: 0 4rem;
          background: ${(props) => props.theme.background0};
          max-width: 1336px;
          width: 100%;
        `}
      >
        <Row style={{ minHeight: 56 }}>
          <Column grow>
            <BackLink />
          </Column>
        </Row>
        <Row gutter={32}>
          <Column grow>
            <GroupBanner {...group} groupSettingsLinks={groupSettingsLinks} />
          </Column>
        </Row>

        <GroupPageMenu
          tabs={tabs}
          hasTabs={hasTabs}
          stickyOffset={72}
          activeTabId={activeTabId}
        />

        <Row
          gutter={32}
          style={{
            marginTop: "3.5rem",
            flexDirection: activeTabId === "info" ? "row" : "row-reverse",
          }}
        >
          <Column grow>
            <R
              {...props}
              groupSettingsLinks={groupSettingsLinks}
              allEvents={allEvents}
              hasTabs={hasTabs}
              onClickMessage={handleClickMessage}
              getMessageURL={getMessageURL}
              goToAgendaTab={goToAgendaTab}
              goToMessagesTab={goToMessagesTab}
            />
          </Column>
          <Column width="320px">
            <GroupUserActions
              {...group}
              groupSettingsLinks={groupSettingsLinks}
            />
            <GroupOrders {...group} />
            <div
              css={`
                background-color: ${(props) => props.theme.text25};
                padding: 1.5rem;
              `}
            >
              <GroupContactCard
                id={group?.id}
                isMessagingEnabled={group?.isMessagingEnabled}
                contact={group?.contact}
                editLinkTo={groupSettingsLinks?.contact}
              />
              {allEvents && allEvents.length > 0 ? (
                <GroupDescription
                  {...group}
                  editLinkTo={groupSettingsLinks?.general}
                />
              ) : null}
              <GroupLinks {...group} editLinkTo={groupSettingsLinks?.links} />
              <GroupFacts {...group} />
              <GroupDonation {...group} />
            </div>
          </Column>
        </Row>

        {activeTabId !== "messages" ? (
          <Row gutter={32}>
            <Column grow>
              {Array.isArray(groupSuggestions) &&
              groupSuggestions.length > 0 ? (
                <GroupSuggestions
                  groups={groupSuggestions}
                  backLink={backLink}
                />
              ) : null}
            </Column>
          </Row>
        ) : null}
      </Container>
      <GroupSettings group={group} basePath={activePathname} />
    </>
  );
};
DesktopGroupPage.propTypes = {
  group: PropTypes.object,
  groupSuggestions: PropTypes.arrayOf(PropTypes.object),
  upcomingEvents: PropTypes.arrayOf(PropTypes.object),
  pastEvents: PropTypes.arrayOf(PropTypes.object),
  allEvents: PropTypes.arrayOf(PropTypes.object),
  backLink: PropTypes.oneOfType([PropTypes.string, PropTypes.object]),
};

export default DesktopGroupPage;
