import React, { useMemo } from "react";
import PropTypes from "prop-types";

import styled from "styled-components";

import StaticToast from "@agir/front/genericComponents/StaticToast";
import QuitEventButton from "./QuitEventButton";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";

import { useSelector } from "@agir/front/globalContext/GlobalContext";
import { getUser } from "@agir/front/globalContext/reducers";
import Link from "@agir/front/app/Link";

const StyledContent = styled.div``;
const StyledJoin = styled.div`
  display: flex;
  align-items: start;
  margin-bottom: 0.5rem;

  & > ${RawFeatherIcon} {
    height: 1.25rem;
    color: ${(props) => props.theme.text500};
  }

  &:last-child {
    margin-bottom: 0;
  }
`;

const StyledWrapper = styled(StaticToast)`
  border-radius: ${(props) => props.theme.borderRadius};
  border-color: lightgrey;
  display: flex;
  flex-direction: column;
  padding: 1rem 1.5rem;

  &:empty {
    display: none;
  }

  && {
    margin-top: 1rem;
    margin-bottom: 0;
  }

  ${StyledContent} {
    flex: 1;
    display: flex;
    align-items: center;
    margin-bottom: 0.5rem;
    justify-content: space-between;
    gap: 0.5rem;

    & div a {
      font-weight: 500;
    }
  }

  ${StyledContent}:last-child {
    margin-bottom: 0;
  }
`;

const RSVP_STATUS = {
  // CONFIRMED
  CO: ({ isPast, rsvpRoute }) => ({
    icon: "check",
    color: "green",
    label: isPast ? (
      "Vous avez participé à cet événement"
    ) : rsvpRoute ? (
      <Link route={rsvpRoute}>Vous participez à l'événement</Link>
    ) : (
      "Vous participez à l'événement"
    ),
  }),
  // CANCELLED
  CA: {
    label: "Vous avez indiqué ne pas pouvoir participer à cet événement",
  },
  // AWAITING_PAYMENT
  AP: ({ isPast, rsvpRoute }) =>
    !isPast
      ? {
          icon: "clock",
          label: rsvpRoute ? (
            <Link route={rsvpRoute}>
              Votre participation est en attente de règlement
            </Link>
          ) : (
            "Votre participation est en attente de règlement"
          ),
        }
      : null,
};

const RSVP = ({ canCancelRSVP, eventPk, status, isPast = false }) => {
  if (!status) {
    return null;
  }

  return (
    <StyledJoin>
      {status.icon && (
        <RawFeatherIcon
          name={status.icon}
          color={status.color}
          style={{ marginRight: "0.5rem" }}
          width="1rem"
          height="1rem"
        />
      )}
      <StyledContent>
        <div>{status.label}</div>
        {!isPast && canCancelRSVP && <QuitEventButton eventPk={eventPk} />}
      </StyledContent>
    </StyledJoin>
  );
};
RSVP.propTypes = {
  canCancelRSVP: PropTypes.bool,
  eventPk: PropTypes.string.isRequired,
  backLink: PropTypes.oneOfType([PropTypes.string, PropTypes.object]),
  isPast: PropTypes.bool,
  status: PropTypes.shape({
    icon: PropTypes.string,
    color: PropTypes.string,
    label: PropTypes.node,
  }),
};

const GroupRSVP = ({ eventPk, group, backLink, isPast = false }) => (
  <StyledJoin>
    <StyledContent>
      <div>
        Votre groupe&nbsp;
        <Link
          route="groupDetails"
          routeParams={{ groupPk: group.id }}
          backLink={backLink}
        >
          {group.name}
        </Link>
        &nbsp;{isPast ? "a participé" : "participe"} à l'événement
      </div>
      {!isPast && group.isManager && (
        <QuitEventButton eventPk={eventPk} group={group} />
      )}
    </StyledContent>
  </StyledJoin>
);
GroupRSVP.propTypes = {
  eventPk: PropTypes.string.isRequired,
  group: PropTypes.shape({
    id: PropTypes.string,
    name: PropTypes.string,
    isManager: PropTypes.bool,
  }),
  backLink: PropTypes.oneOfType([PropTypes.string, PropTypes.object]),
  isPast: PropTypes.bool,
};

const JoiningDetails = (props) => {
  const {
    id,
    canCancelRSVP,
    rsvp,
    groups,
    logged,
    backLink,
    rsvpRoute,
    isPast = false,
  } = props;

  const user = useSelector(getUser);
  const managingGroupsAttendees = useMemo(() => {
    if (!user?.groups) {
      return [];
    }

    if (!Array.isArray(groups)) {
      return user.groups.filter((group) => group.isManager);
    }

    return user.groups.filter(
      (group) => group.isManager && groups.some((g) => g.id === group.id),
    );
  }, [user, groups]);

  const rsvpStatus = useMemo(() => {
    const statusConfig = rsvp && RSVP_STATUS[rsvp];
    if (!statusConfig) {
      return null;
    }
    return typeof statusConfig === "function"
      ? statusConfig({ isPast, rsvpRoute })
      : statusConfig;
  }, [isPast, rsvp, rsvpRoute]);

  if (!logged) {
    return null;
  }

  if (!rsvp && managingGroupsAttendees.length === 0) {
    return null;
  }

  return (
    <StyledWrapper $color={rsvpStatus?.color || "text500"}>
      {logged && rsvp && (
        <RSVP
          eventPk={id}
          canCancelRSVP={canCancelRSVP}
          isPast={isPast}
          status={rsvpStatus}
        />
      )}
      {managingGroupsAttendees.map((group) => (
        <GroupRSVP
          key={group.id}
          eventPk={id}
          group={group}
          backLink={backLink}
          isPast={isPast}
        />
      ))}
    </StyledWrapper>
  );
};
JoiningDetails.propTypes = {
  id: PropTypes.string.isRequired,
  canCancelRSVP: PropTypes.bool,
  rsvp: PropTypes.string,
  groups: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.string,
      name: PropTypes.string,
      isManager: PropTypes.bool,
    }),
  ),
  logged: PropTypes.bool,
  backLink: PropTypes.oneOfType([PropTypes.string, PropTypes.object]),
  rsvpRoute: PropTypes.string,
  isPast: PropTypes.bool,
};

export default JoiningDetails;
