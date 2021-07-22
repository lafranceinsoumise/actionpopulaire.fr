import PropTypes from "prop-types";
import React from "react";
import useSWR from "swr";

import styled from "styled-components";

import Spacer from "@agir/front/genericComponents/Spacer.js";
import ShareLink from "@agir/front/genericComponents/ShareLink.js";
import Link from "@agir/front/app/Link";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";

import HeaderPanel from "@agir/front/genericComponents/ObjectManagement/HeaderPanel.js";
import MemberList from "@agir/groups/groupPage/GroupSettings/GroupMemberList";

const StyledLink = styled(Link)`
  font-size: 13px;
  display: inline-flex;
  align-items: center;
`;

const BlockTitle = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;

  h3 {
    margin: 0;
    margin-top: 0.5rem;
    margin-bottom: 0.5rem;
  }

  > div {
    margin-top: 3px;
  }
`;

const EventParticipants = (props) => {
  const { onBack, illustration, eventPk } = props;

  console.log("event general with pk : ", eventPk);

  const group = {
    email: "pole@group.com",
    displayName: "Pôle groupe d'action",
  };
  const members = [
    { email: "pascal@preprod.com", displayName: "Pascal Preprod" },
    { email: "pascal@preprod.com", displayName: "Pascal Preprod" },
  ];

  const { data: event, mutate } = useSWR();
  // getGroupPageEndpoint("getGroup", { groupPk })

  return (
    <>
      <HeaderPanel onBack={onBack} illustration={illustration} />
      <BlockTitle>
        <h3>Participant·es</h3>
        <div>
          <StyledLink href={"#"}>
            <RawFeatherIcon name="mail" height="13px" />
            Inviter à l’événement
          </StyledLink>
          <StyledLink href={"#"} style={{ marginLeft: "10px" }}>
            <RawFeatherIcon name="settings" height="13px" />
            Inviter à co-organiser
          </StyledLink>
        </div>
      </BlockTitle>

      <Spacer size="1rem" />
      <ShareLink
        label="Copier les e-mails des membres"
        color="primary"
        url={members?.map(({ email }) => email).join(", ") || ""}
        $wrap
      />

      <Spacer size="1rem" />
      <MemberList key={0} members={[group]} />
      <Spacer size="1rem" />
      <MemberList key={1} members={members} />
      <Spacer size="1rem" />
    </>
  );
};
EventParticipants.propTypes = {
  onBack: PropTypes.func,
  illustration: PropTypes.string,
  eventPk: PropTypes.string,
};
export default EventParticipants;
