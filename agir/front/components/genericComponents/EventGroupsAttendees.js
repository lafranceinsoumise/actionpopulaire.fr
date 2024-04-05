import PropTypes from "prop-types";
import React from "react";

import styled from "styled-components";
import * as style from "@agir/front/genericComponents/_variables.scss";

import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";

import { useSelector } from "@agir/front/globalContext/GlobalContext";
import { getUser } from "@agir/front/globalContext/reducers";

const StyledGroupsAttendees = styled.div`
  padding: 10px;
  background-color: ${style.primary50};
  display: flex;
  align-items: center;
  flex-wrap: wrap;
`;

export const EventGroupsAttendees = ({ groupsAttendees, isPast }) => {
  const user = useSelector(getUser);

  if (!groupsAttendees?.length) {
    return null;
  }

  const userGroupsId = Array.isArray(user?.groups)
    ? user.groups.map((group) => group.id)
    : [];
  const userGroupsAttendees = Array.isArray(groupsAttendees)
    ? groupsAttendees.filter((group) => userGroupsId.includes(group.id))
    : [];

  if (!userGroupsAttendees.length) {
    return null;
  }

  return (
    <StyledGroupsAttendees>
      <RawFeatherIcon
        name="users"
        width="1rem"
        height="1rem"
        style={{ marginRight: "0.5rem" }}
      />
      Votre groupe&nbsp;<strong>{userGroupsAttendees[0].name}</strong>
      &nbsp;
      {userGroupsAttendees.length > 1 ? (
        <>
          et {userGroupsAttendees.length - 1} autres groupes&nbsp;
          {isPast ? "y ont participé" : "y participent"}
        </>
      ) : (
        <>{isPast ? "y a participé" : "y participe"}</>
      )}
    </StyledGroupsAttendees>
  );
};

EventGroupsAttendees.propTypes = {
  groupsAttendees: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.string,
      name: PropTypes.string,
      isManager: PropTypes.bool,
    }),
  ),
  isPast: PropTypes.bool,
};

export default EventGroupsAttendees;
