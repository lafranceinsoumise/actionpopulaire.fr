import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

import { Column, Container, Row } from "@agir/front/genericComponents/grid";
import Skeleton from "@agir/front/genericComponents/Skeleton";
import Tabs from "@agir/front/genericComponents/Tabs";
import ShareCard from "@agir/front/genericComponents/ShareCard";

import GroupBanner from "../GroupBanner";

import GroupLocation from "../GroupLocation";
import GroupJoin from "../GroupJoin";
import GroupContactCard from "../GroupContactCard";
import GroupDescription from "../GroupDescription";
import GroupLinks from "../GroupLinks";
import GroupFacts from "../GroupFacts";
import GroupDonation from "../GroupDonation";
import GroupSuggestions from "../GroupSuggestions";

export const MobileGroupPageSkeleton = () => (
  <Container style={{ margin: "2rem auto", padding: "0 1rem" }}>
    <Row>
      <Column stack>
        <Skeleton />
      </Column>
    </Row>
  </Container>
);

const tabs = [
  {
    id: "info",
    label: "Présentation",
  },
  {
    id: "agenda",
    label: "Agenda",
  },
];

const Tab = styled.div`
  max-width: 100%;
  margin: 0;
  padding: 0;
`;

const MobileGroupPage = (props) => {
  const { group, groupSuggestions } = props;

  if (!group) {
    return null;
  }

  return (
    <Container
      style={{
        margin: 0,
        padding: "0 0 3.5rem",
      }}
    >
      <GroupBanner {...group} />
      <GroupJoin url={!group.isMember ? "#join" : ""} />
      <Tabs tabs={tabs}>
        <Tab id="info">
          <h3
            style={{
              margin: 0,
              padding: "1.5rem 1rem",
              height: 316,
              background: style.black25,
            }}
          >
            Agenda
          </h3>
          <GroupContactCard {...group} />
          <GroupDescription {...group} />
          <GroupLinks {...group} />
          <GroupFacts {...group} />
          <GroupLocation {...group} />
          {group.routes && group.routes.donations && (
            <GroupDonation url={group.routes.donations} />
          )}
          <ShareCard />

          {Array.isArray(groupSuggestions) && groupSuggestions.length > 0 ? (
            <div style={{ marginTop: 71, marginBottom: 71 }}>
              <GroupSuggestions groups={groupSuggestions} />
            </div>
          ) : null}
        </Tab>
        <Tab id="agenda">
          <h3
            style={{
              margin: 0,
              padding: "1.5rem 1rem",
              height: 316,
              background: style.black25,
            }}
          >
            Événements à venir
          </h3>
          <h3
            style={{
              margin: 0,
              padding: "1.5rem 1rem",
              height: 316,
              background: style.black25,
            }}
          >
            Événements passés
          </h3>
        </Tab>
      </Tabs>
    </Container>
  );
};
MobileGroupPage.propTypes = {
  group: PropTypes.shape({
    isMember: PropTypes.bool,
    isManager: PropTypes.bool,
    routes: PropTypes.shape({
      donations: PropTypes.string,
    }),
  }),
  groupSuggestions: PropTypes.arrayOf(PropTypes.object),
};
export default MobileGroupPage;
