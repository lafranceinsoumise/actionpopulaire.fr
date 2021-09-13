import PropTypes from "prop-types";
import React, { useMemo } from "react";
import useSWR from "swr";
import * as api from "@agir/events/common/api";

import styled from "styled-components";

import Spacer from "@agir/front/genericComponents/Spacer";
import ShareLink from "@agir/front/genericComponents/ShareLink";
import Link from "@agir/front/app/Link";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";

import HeaderPanel from "@agir/front/genericComponents/ObjectManagement/HeaderPanel";
import MemberList from "./EventMemberList";

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

  const { data: event, mutate } = useSWR(
    api.getEventEndpoint("getDetailAdvanced", { eventPk })
  );

  const participants = useMemo(() => event?.participants || [], [event]);
  const organizers = useMemo(() => event?.organizers || [], [event]);
  const allParticipants = participants.concat(organizers);

  return (
    <>
      <HeaderPanel onBack={onBack} illustration={illustration} />
      <BlockTitle>
        <h3>{allParticipants.length} Participant·es</h3>
        <div>
          <StyledLink to="../organisation/" style={{ marginLeft: "10px" }}>
            <RawFeatherIcon name="settings" height="13px" />
            Inviter à co-organiser
          </StyledLink>
        </div>
      </BlockTitle>

      <Spacer size="1rem" />
      <ShareLink
        label="Copier les e-mails des participant·es"
        color="primary"
        url={allParticipants.map(({ email }) => email).join(", ") || ""}
        $wrap
      />

      <Spacer size="2rem" />
      <MemberList key={1} members={allParticipants} />
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
