import PropTypes from "prop-types";
import React, { useMemo } from "react";
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
  margin: 20px 0 20px -1rem;

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
  } = props;

  const hasEvents = useMemo(() => {
    const past = Array.isArray(pastEvents) ? pastEvents : [];
    const upcoming = Array.isArray(upcomingEvents) ? upcomingEvents : [];
    return past.length + upcoming.length > 0;
  }, [upcomingEvents, pastEvents]);

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
        <Row>
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
      <Row gutter={32} style={{ marginBottom: "3.5rem" }}>
        <Column grow>
          <GroupBanner {...group} />
        </Column>
      </Row>

      <Row gutter={32}>
        <Column grow>
          {hasEvents ? (
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
};
export default DesktopGroupPage;
