import React, { useMemo } from "react";
import PropTypes from "prop-types";

import styled from "styled-components";
import style from "@agir/front/genericComponents/_variables.scss";

import StaticToast from "@agir/front/genericComponents/StaticToast";
import QuitEventButton from "./QuitEventButton";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";

import { useSelector } from "@agir/front/globalContext/GlobalContext";
import { getUser } from "@agir/front/globalContext/reducers";
import Link from "@agir/front/app/Link";

const StyledContent = styled.div``;
const StyledJoin = styled.div`
  display: flex;
  margin-bottom: 0.5rem;

  &:last-child {
    margin-bottom: 0;
  }
`;

const GreenToast = styled(StaticToast)`
  border-radius: ${style.borderRadius};
  border-color: lightgrey;
  display: flex;
  flex-direction: column;

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

const RSVP = ({ hasPrice, eventPk, rsvpRoute, isPast = false }) => (
  <StyledJoin>
    <RawFeatherIcon
      name="check"
      color="green"
      style={{ marginRight: "0.5rem" }}
    />
    <StyledContent>
      <div>
        {isPast ? (
          "Vous avez participé à l'événement"
        ) : rsvpRoute ? (
          <Link route={rsvpRoute}>Vous participez à l'événement</Link>
        ) : (
          "Vous participez à l'événement"
        )}
      </div>
      {!hasPrice && !isPast && <QuitEventButton eventPk={eventPk} />}
    </StyledContent>
  </StyledJoin>
);
RSVP.propTypes = {
  hasPrice: PropTypes.bool,
  eventPk: PropTypes.string.isRequired,
  backLink: PropTypes.oneOfType([PropTypes.string, PropTypes.object]),
  rsvpRoute: PropTypes.string,
  isPast: PropTypes.bool,
};

const GroupRSVP = ({ eventPk, group, backLink, isPast = false }) => (
  <StyledJoin>
    <RawFeatherIcon
      name="check"
      color="green"
      style={{ marginRight: "0.5rem" }}
    />
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
    hasPrice,
    rsvped,
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

  if ((!rsvped || !logged) && !managingGroupsAttendees?.length) {
    return null;
  }

  return (
    <GreenToast $color="green">
      {logged && rsvped && (
        <RSVP
          eventPk={id}
          hasPrice={hasPrice}
          rsvpRoute={rsvpRoute}
          isPast={isPast}
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
    </GreenToast>
  );
};
JoiningDetails.propTypes = {
  id: PropTypes.string.isRequired,
  hasPrice: PropTypes.bool,
  rsvped: PropTypes.bool,
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
