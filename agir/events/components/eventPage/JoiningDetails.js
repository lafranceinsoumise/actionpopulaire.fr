import React from "react";
import PropTypes from "prop-types";

import styled from "styled-components";
import style from "@agir/front/genericComponents/_variables.scss";

import StaticToast from "@agir/front/genericComponents/StaticToast";
import QuitEventButton from "./QuitEventButton";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";

const StyledJoinEntry = styled.div``;

const GreenToast = styled(StaticToast)`
  border-radius: ${style.borderRadius};
  border-color: lightgrey;
  display: flex;
  flex-direction: column;

  && {
    margin-top: 1rem;
  }

  ${StyledJoinEntry} {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.5rem;
    flex-wrap: wrap;

    div {
      display: flex;
    }
  }

  ${StyledJoinEntry}:last-child {
    margin-bottom: 0;
  }
`;

const JoiningDetails = ({ id, hasPrice, rsvped, groups, logged }) => {
  if ((!rsvped || !logged) && !groups?.length) {
    return null;
  }
  return (
    <GreenToast $color="green">
      {logged && rsvped && (
        <StyledJoinEntry>
          <div>
            <RawFeatherIcon name="check" color="green" /> &nbsp;Vous participez
            à l'événement
          </div>
          {!hasPrice && <QuitEventButton eventPk={id} />}
        </StyledJoinEntry>
      )}

      {groups.map((group) => (
        <StyledJoinEntry key={group.id}>
          <div>
            <RawFeatherIcon name="check" color="green" /> &nbsp;
            <b>{group.name}</b>&nbsp;participe à l'événement
          </div>
          {group.isManager && <QuitEventButton eventPk={id} group={group} />}
        </StyledJoinEntry>
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
