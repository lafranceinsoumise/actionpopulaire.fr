import React from "react";
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
    margin-top: 0.5rem;
  }

  ${StyledContent} {
    flex: 1;
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    margin-bottom: 0.5rem;

    justify-content: space-between;
    @media (max-width: ${style.collapse}px) {
      flex-direction: column;
      align-items: baseline;
    }
  }

  ${StyledContent}:last-child {
    margin-bottom: 0;
  }
`;

const Joined = ({ hasPrice, eventPk, group }) => (
  <StyledJoin>
    <RawFeatherIcon
      name="check"
      color="green"
      style={{ marginRight: "0.5rem" }}
    />
    <StyledContent>
      <div>
        {!group ? (
          "Vous participez à l'événement"
        ) : (
          <>
            Votre groupe&nbsp;
            <Link route="groupDetails" routeParams={{ groupPk: group.id }}>
              <b>{group.name}</b>
            </Link>
            &nbsp;participe à l'événement
          </>
        )}
      </div>
      {!group
        ? !hasPrice && <QuitEventButton eventPk={eventPk} />
        : group.isManager && (
            <QuitEventButton eventPk={eventPk} group={group} />
          )}
    </StyledContent>
  </StyledJoin>
);
Joined.propTypes = {
  hasPrice: PropTypes.bool,
  eventPk: PropTypes.string.isRequired,
  group: PropTypes.shape({
    id: PropTypes.string,
    name: PropTypes.string,
    isManager: PropTypes.bool,
  }),
};

const JoiningDetails = ({ id, hasPrice, rsvped, groups, logged }) => {
  const user = useSelector(getUser);
  const groupsId = groups?.map((group) => group.id) || [];

  // Get groups attendees from user only
  const userGroupsAttendees = user?.groups.filter((group) =>
    groupsId.includes(group.id)
  );

  if ((!rsvped || !logged) && !groups?.length) {
    return null;
  }
  return (
    <GreenToast $color="green">
      {logged && rsvped && <Joined eventPk={id} hasPrice={hasPrice} />}
      {userGroupsAttendees.map((group) => (
        <Joined key={group.id} eventPk={id} hasPrice={hasPrice} group={group} />
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
    })
  ),
  logged: PropTypes.bool,
};

export default JoiningDetails;
