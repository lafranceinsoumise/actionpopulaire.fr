import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import { routeConfig } from "@agir/front/app/routes.config";
import style from "@agir/front/genericComponents/_variables.scss";

import FeatherIcon from "@agir/front/genericComponents/FeatherIcon";
import Link from "@agir/front/app/Link";

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

const GroupLine = ({ id, name, eventCount, membersCount, isDetailed }) => (
  <StyledGroupLine>
    <Link
      aria-label={name}
      to={routeConfig.groupDetails.getLink({ groupPk: id })}
    >
      <GroupIcon>
        <FeatherIcon name="users" />
      </GroupIcon>
    </Link>

    <div style={{ paddingLeft: "1rem" }}>
      <h3 style={{ marginTop: 2, marginBottom: 2 }}>
        <Link to={routeConfig.groupDetails.getLink({ groupPk: id })}>
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
  name: PropTypes.string.isRequired,
  description: PropTypes.string,
  eventCount: PropTypes.number,
  membersCount: PropTypes.number,
  isDetailed: PropTypes.bool,
};

const GroupsCard = ({ title, groups, isDetailed }) => {
  if (!groups?.length) {
    return <></>;
  }
  return (
    <StyledContainer>
      <h3>{title}</h3>
      {groups.map((group) => (
        <GroupLine {...group} isDetailed={isDetailed} />
      ))}
    </StyledContainer>
  );
};

GroupsCard.propTypes = {
  title: PropTypes.string,
  groups: PropTypes.array,
  isDetailed: PropTypes.bool,
};

export default GroupsCard;
