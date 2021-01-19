import PropTypes from "prop-types";
import React, { useCallback, useMemo, useState } from "react";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";
import Link from "@agir/front/app/Link";
import { Column, Container, Row } from "@agir/front/genericComponents/grid";
import Skeleton from "@agir/front/genericComponents/Skeleton";
import ShareCard from "@agir/front/genericComponents/ShareCard";

import GroupBanner from "../GroupBanner";
import GroupLocation from "../GroupLocation";
import GroupUserActions from "../GroupUserActions";
import GroupContactCard from "../GroupContactCard";
import GroupDescription from "../GroupDescription";
import GroupLinks from "../GroupLinks";
import GroupFacts from "../GroupFacts";
import GroupDonation from "../GroupDonation";
import GroupSuggestions from "../GroupSuggestions";
import GroupEventList from "../GroupEventList";

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

const StyledMenu = styled.nav`
  position: sticky;
  z-index: 1;
  top: -1px;
  left: 0;
  right: 0;
  display: flex;
  flex-flow: row nowrap;
  justify-content: center;
  padding: 0;
  margin: 0 1rem;
  background-color: white;
  box-shadow: inset 0px -1px 0px #dfdfdf;

  button {
    flex: 0 1 auto;
    padding: 0 1rem;
    background-color: transparent;
    border: none;
    height: 80px;
    cursor: pointer;
    transition: all 200ms ease-in-out;
    box-shadow: none;
    color: ${style.black1000};
    white-space: nowrap;

    &[data-active],
    &:hover,
    &:focus {
      color: ${style.primary500};
      border: none;
      outline: none;
    }

    &[data-active] {
      background-size: 100%;
      box-shadow: 0 -3px 0 ${style.primary500} inset;
    }
  }
`;

export const DesktopGroupPageSkeleton = () => (
  <Container
    style={{
      margin: "4rem auto",
      padding: "0 4rem",
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
  const {
    backLink,
    group,
    groupSuggestions,
    upcomingEvents,
    pastEvents,
    isLoadingPastEvents,
    loadMorePastEvents,
    pastEventReports,
  } = props;

  const hasEvents = useMemo(() => {
    const past = Array.isArray(pastEvents) ? pastEvents : [];
    const upcoming = Array.isArray(upcomingEvents) ? upcomingEvents : [];
    return past.length + upcoming.length > 0;
  }, [upcomingEvents, pastEvents]);

  const hasTabs = useMemo(
    () =>
      !!hasEvents &&
      Array.isArray(pastEventReports) &&
      pastEventReports.length > 0,
    [hasEvents, pastEventReports]
  );

  const [activeTab, setActiveTab] = useState("agenda");

  const handleTabClick = useCallback((e) => {
    setActiveTab(e.target.dataset.tab);
  }, []);

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
      {hasTabs ? (
        <StyledMenu>
          <button
            data-tab="agenda"
            data-active={activeTab === "agenda" || undefined}
            disabled={activeTab === "agenda"}
            onClick={handleTabClick}
          >
            Agenda
          </button>
          <button
            data-tab="reports"
            data-active={activeTab === "reports" || undefined}
            disabled={activeTab === "reports"}
            onClick={handleTabClick}
          >
            Compte-rendus
          </button>
        </StyledMenu>
      ) : null}

      <Row gutter={32} style={{ marginTop: "3.5rem" }}>
        <Column grow>
          {hasEvents ? (
            <>
              {activeTab === "agenda" ? (
                <>
                  <GroupEventList
                    title="Événements à venir"
                    events={upcomingEvents}
                  />
                  <GroupEventList
                    title="Événements passés"
                    events={pastEvents}
                    loadMore={loadMorePastEvents}
                    isLoading={isLoadingPastEvents}
                  />
                  <GroupLocation {...group} />
                  <ShareCard title="Partager le lien du groupe" />
                </>
              ) : null}
              {activeTab === "reports" ? (
                <GroupEventList
                  title="Comptes-rendus"
                  events={pastEventReports}
                />
              ) : null}
            </>
          ) : (
            <>
              <GroupDescription {...group} maxHeight="auto" />
              <ShareCard title="Inviter vos ami·es à rejoindre le groupe" />
              <GroupLocation {...group} />
            </>
          )}
        </Column>

        <Column width="460px">
          <GroupUserActions {...group} />
          <GroupContactCard {...group} />
          {hasEvents && <GroupDescription {...group} />}
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
  isConnected: PropTypes.bool,
  group: PropTypes.shape({
    isMember: PropTypes.bool,
    isManager: PropTypes.bool,
    routes: PropTypes.shape({
      donations: PropTypes.string,
    }),
  }),
  groupSuggestions: PropTypes.arrayOf(PropTypes.object),
  upcomingEvents: PropTypes.arrayOf(PropTypes.object),
  pastEvents: PropTypes.arrayOf(PropTypes.object),
  isLoadingPastEvents: PropTypes.bool,
  loadMorePastEvents: PropTypes.func,
  pastEventReports: PropTypes.arrayOf(PropTypes.object),
};
export default DesktopGroupPage;
