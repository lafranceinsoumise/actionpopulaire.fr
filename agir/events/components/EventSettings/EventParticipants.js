import * as api from "@agir/events/common/api";
import PropTypes from "prop-types";
import React, { useMemo } from "react";
import useSWR from "swr";

import { routeConfig as globalRouteConfig } from "@agir/front/app/routes.config";
import styled from "styled-components";
import { getMenuRoute, routeConfig } from "./routes.config";

import Link from "@agir/front/app/Link";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";
import HeaderPanel from "@agir/front/genericComponents/ObjectManagement/HeaderPanel";
import ShareLink from "@agir/front/genericComponents/ShareLink";
import Spacer from "@agir/front/genericComponents/Spacer";
import MemberList from "./EventMemberList";
import GroupItem from "./GroupItem";
import GroupList from "./GroupList";

const StyledLink = styled(Link)``;

const BlockTitle = styled.div`
  display: flex;
  flex-flow: row nowrap;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;

  & > * {
    margin: 0;
    flex: 0 0 mincontent;
  }

  h3 {
    flex: 1 1 auto;
    margin-top: 0.5rem;
    margin-bottom: 0.5rem;
  }

  ${StyledLink} {
    font-size: 0.75rem;
    display: inline-flex;
    flex-flow: row nowrap;
    align-items: center;
    justify-content: end;
    gap: 0.25rem;

    & > * {
      flex: 0 0 auto;
    }
  }
`;

const EventParticipants = (props) => {
  const { onBack, illustration, eventPk } = props;

  const { data: event } = useSWR(
    api.getEventEndpoint("getDetailAdvanced", { eventPk }),
  );

  const [participants, unavailable] = useMemo(() => {
    const participants = [];
    const unavailable = [];

    Array.isArray(event?.participants) &&
      event.participants.forEach((person) => {
        person.unavailable
          ? unavailable.push(person)
          : participants.push(person);
      });

    return [participants, unavailable];
  }, [event]);
  const groupsAttendees = useMemo(() => event?.groupsAttendees || [], [event]);
  const severalGroups = groupsAttendees.length > 1;

  const menuRoute = getMenuRoute(
    globalRouteConfig.eventDetails.getLink({ eventPk }),
  ).path;
  const organizationLink = `${menuRoute}${routeConfig.organisation.path}`;

  return (
    <>
      <HeaderPanel onBack={onBack} illustration={illustration} />
      <BlockTitle>
        <h3>{participants.length} participant·es</h3>
        {!event?.isPast && (
          <StyledLink to={organizationLink}>
            <RawFeatherIcon name="settings" height="1rem" />
            Inviter à co-organiser
          </StyledLink>
        )}
      </BlockTitle>
      <ShareLink
        label="Copier les e-mails"
        color="primary"
        url={participants.map(({ email }) => email).join(", ") || ""}
        $wrap
      />
      <Spacer size="1rem" />
      <MemberList key={1} members={participants} />
      <Spacer size="1.5rem" />
      {groupsAttendees.length > 0 && (
        <>
          <BlockTitle>
            <h3>
              {groupsAttendees.length} groupe{severalGroups && "s"} participant
              {severalGroups && "s"}
            </h3>
          </BlockTitle>
          Les groupes ayant indiqué leur participation. Ils ne sont pas indiqués
          co-organisateurs de l'événement. Vous pouvez les inviter à
          co-organiser cet événement depuis l'onglet&nbsp;
          <Link to={organizationLink} style={{ display: "inline-block" }}>
            <RawFeatherIcon name="settings" height="14px" />
            Organisation
          </Link>
          .
          <Spacer size="1rem" />
          <GroupList>
            {groupsAttendees.map((group) => (
              <GroupItem
                key={group.id}
                id={group.id}
                name={group.name}
                image={group.image}
                isLinked
              />
            ))}
          </GroupList>
        </>
      )}
      {unavailable.length > 0 && (
        <>
          <Spacer size="1.5rem" />
          <BlockTitle>
            <h3>
              {unavailable.length} personne{unavailable.length > 1 && "s"}{" "}
              indisponible
              {unavailable.length > 1 && "s"}
            </h3>
          </BlockTitle>
          Les personnes ayant indiqué ne pas pouvoir participer à l'événement.
          <Spacer size="1rem" />
          <MemberList key={1} members={unavailable} />
        </>
      )}
    </>
  );
};
EventParticipants.propTypes = {
  onBack: PropTypes.func,
  illustration: PropTypes.string,
  eventPk: PropTypes.string,
};
export default EventParticipants;
