import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import { routeConfig } from "@agir/front/app/routes.config";
import { routeConfig as eventRouteConfig } from "@agir/events/EventSettings/routes.config";

import style from "@agir/front/genericComponents/_variables.scss";

import FeatherIcon from "@agir/front/genericComponents/FeatherIcon";
import Link from "@agir/front/app/Link";
import Button from "@agir/front/genericComponents/Button";
import AddGroupAttendee from "@agir/events/eventPage/AddGroupAttendee";

const GroupIcon = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  width: 3rem;
  height: 3rem;
  margin: 0;
  padding: 0;
  border-radius: 100%;
  background-color: ${(props) => props.theme.primary500};
  color: white;
`;

const StyledGroupLine = styled.div`
  display: flex;
  align-items: center;
  padding-top: 10px;
  padding-bottom: 10px;
`;

const StyledContainer = styled.div`
  display: flex;
  flex-direction: column;
  padding: 24px;
  border: 1px solid ${style.black100};

  @media (min-width: ${style.collapse}px) {
    border-radius: ${style.borderRadius};
  }

  a {
    color: inherit;
  }

  h3 {
    margin-top: 0;
    margin-bottom: 1rem;
  }
`;

const GroupLine = ({
  id,
  name,
  eventCount,
  membersCount,
  isDetailed,
  backLink,
}) => (
  <StyledGroupLine>
    <Link
      aria-label={name}
      route="groupDetails"
      routeParams={{ groupPk: id }}
      backLink={backLink}
    >
      <GroupIcon>
        <FeatherIcon name="users" />
      </GroupIcon>
    </Link>
    <div style={{ paddingLeft: "1rem" }}>
      <h3 style={{ marginTop: 2, marginBottom: 2 }}>
        <Link
          route="groupDetails"
          routeParams={{ groupPk: id }}
          backLink={backLink}
        >
          {name}
        </Link>
      </h3>
      {isDetailed && (
        <small style={{ color: style.black500 }}>
          {eventCount} événement{eventCount > 1 ? "s" : ""} &bull;{" "}
          {membersCount} membre{membersCount > 1 ? "s" : ""}
        </small>
      )}
    </div>
  </StyledGroupLine>
);
GroupLine.propTypes = {
  id: PropTypes.string.isRequired,
  name: PropTypes.string.isRequired,
  eventCount: PropTypes.number,
  membersCount: PropTypes.number,
  isDetailed: PropTypes.bool,
  backLink: PropTypes.oneOfType([PropTypes.string, PropTypes.object]),
};

export const GroupsOrganizingCard = ({
  groups,
  isDetailed,
  eventPk,
  isOrganizer,
  isPast,
  backLink,
}) => {
  if (!groups?.length) {
    return null;
  }

  const coorganizeLink =
    !!eventPk && isOrganizer
      ? `${routeConfig.eventSettings.getLink({
          eventPk,
        })}${eventRouteConfig.organisation.path}`
      : false;

  return (
    <StyledContainer>
      <h3>Organisé par</h3>
      {groups.map((group) => (
        <GroupLine
          key={group.id}
          isDetailed={isDetailed}
          backLink={backLink}
          {...group}
        />
      ))}
      {coorganizeLink && !isPast && (
        <Button
          link
          to={coorganizeLink}
          style={{ width: "fit-content", marginTop: "1rem" }}
        >
          Inviter à co-organiser
        </Button>
      )}
    </StyledContainer>
  );
};

GroupsOrganizingCard.propTypes = {
  groups: PropTypes.array,
  isDetailed: PropTypes.bool,
  eventPk: PropTypes.string,
  isOrganizer: PropTypes.bool,
  isPast: PropTypes.bool,
  backLink: PropTypes.oneOfType([PropTypes.string, PropTypes.object]),
};

export const GroupsJoiningCard = ({
  groups,
  groupsAttendees,
  eventPk,
  isPast,
  backLink,
}) => {
  if (!groupsAttendees?.length) {
    return null;
  }

  return (
    <StyledContainer>
      <h3>
        {!isPast ? "Mes groupes y participent" : "Mes groupes y ont participé"}
      </h3>
      {groupsAttendees.map((group) => (
        <GroupLine key={group.id} backLink={backLink} {...group} />
      ))}
      {eventPk && !isPast && (
        <AddGroupAttendee
          id={eventPk}
          groups={groups}
          groupsAttendees={groupsAttendees}
          style={{ width: "fit-content", marginTop: "1rem" }}
        />
      )}
    </StyledContainer>
  );
};

GroupsJoiningCard.propTypes = {
  groups: PropTypes.array,
  groupsAttendees: PropTypes.array,
  eventPk: PropTypes.string,
  isPast: PropTypes.bool,
  backLink: PropTypes.oneOfType([PropTypes.string, PropTypes.object]),
};
