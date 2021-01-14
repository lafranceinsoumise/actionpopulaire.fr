import PropTypes from "prop-types";
import React from "react";

import { Column, Container, Row } from "@agir/front/genericComponents/grid";
import Skeleton from "@agir/front/genericComponents/Skeleton";
import ShareCard from "@agir/front/genericComponents/ShareCard";

import GroupBanner from "../GroupBanner";
import GroupAdminBar from "../GroupAdminBar";
import GroupLocation from "../GroupLocation";
import GroupJoin from "../GroupJoin";
import GroupContactCard from "../GroupContactCard";
import GroupDescription from "../GroupDescription";
import GroupLinks from "../GroupLinks";
import GroupFacts from "../GroupFacts";
import GroupDonation from "../GroupDonation";
import GroupSuggestions from "../GroupSuggestions";

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
  const { group, groupSuggestions } = props;

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
      <Row gutter={32} style={{ marginBottom: "3.5rem" }}>
        <Column grow>
          <GroupBanner {...group} />
          {group.isManager && <GroupAdminBar {...group} />}
        </Column>
      </Row>

      <Row gutter={32}>
        <Column grow>
          <h3 style={{ height: 300 }}>Événements à venir</h3>
          <h3 style={{ height: 300 }}>Événements passés</h3>
          <GroupLocation {...group} />
          <ShareCard />
        </Column>

        <Column width="460px">
          <GroupJoin url={!group.isMember ? "#join" : ""} />
          <GroupContactCard {...group} />
          <GroupDescription {...group} />
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
  group: PropTypes.shape({
    isMember: PropTypes.bool,
    isManager: PropTypes.bool,
    routes: PropTypes.shape({
      donations: PropTypes.string,
    }),
  }),
  groupSuggestions: PropTypes.arrayOf(PropTypes.object),
};
export default DesktopGroupPage;
