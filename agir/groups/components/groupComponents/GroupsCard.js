import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import { routeConfig } from "@agir/front/app/routes.config";
import { routeConfig as eventRouteConfig } from "@agir/events/EventSettings/routes.config";

import FeatherIcon from "@agir/front/genericComponents/FeatherIcon";
import Link from "@agir/front/app/Link";
import AddGroupAttendee from "@agir/events/eventPage/AddGroupAttendee";
import GroupPageCard from "@agir/groups/groupPage/GroupPageCard";
import Spacer from "@agir/front/genericComponents/Spacer";

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
  color: ${(props) => props.theme.background0};
`;

const StyledGroupLine = styled.div`
  display: flex;
  align-items: center;
  padding-top: 10px;
  padding-bottom: 10px;
`;

const StyledCard = styled(GroupPageCard)`
  && {
    display: flex;
    flex-direction: column;
    box-shadow: none;
    padding: 1.5rem;
    margin: 2rem 0;

    @media (max-width: ${(props) => props.theme.collapse}px) {
      margin: 0;
    }

    h4 {
      font-size: 1.125rem;
      font-weight: 600;
      line-height: 1.5;

      @media (max-width: ${(props) => props.theme.collapse}px) {
        font-size: 0.875rem;
        font-weight: 700;
      }
    }

    a {
      color: inherit;
    }
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
        <small
          css={`
            color: ${(props) => props.theme.text500};
          `}
        >
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
  backLink,
}) => {
  if (!Array.isArray(groups) || groups.length === 0) {
    return null;
  }

  const editLink =
    !!eventPk && isOrganizer
      ? `${routeConfig.eventSettings.getLink({
          eventPk,
        })}${eventRouteConfig.organisation.path}`
      : "";

  return (
    <StyledCard outlined title="Organisé par" editLinkTo={editLink}>
      {groups.map((group) => (
        <GroupLine
          key={group.id}
          isDetailed={isDetailed}
          backLink={backLink}
          {...group}
        />
      ))}
    </StyledCard>
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
    <StyledCard
      outlined
      title={
        !isPast ? "Mes groupes y participent" : "Mes groupes y ont participé"
      }
    >
      {groupsAttendees.map((group) => (
        <GroupLine key={group.id} backLink={backLink} {...group} />
      ))}
      <Spacer size="1rem" />
      {eventPk && !isPast && (
        <AddGroupAttendee
          id={eventPk}
          groups={groups}
          groupsAttendees={groupsAttendees}
          style={{ width: "fit-content", marginTop: "1rem" }}
        />
      )}
    </StyledCard>
  );
};

GroupsJoiningCard.propTypes = {
  groups: PropTypes.array,
  groupsAttendees: PropTypes.array,
  eventPk: PropTypes.string,
  isPast: PropTypes.bool,
  backLink: PropTypes.oneOfType([PropTypes.string, PropTypes.object]),
};
