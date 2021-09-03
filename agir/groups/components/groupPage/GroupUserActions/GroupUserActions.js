import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

import AnonymousActions from "./AnonymousActions";
import NonMemberActions from "./NonMemberActions";
import FollowerActions from "./FollowerActions";
import MemberActions from "./MemberActions";
import ManagerActions from "./ManagerActions";

const StyledContent = styled.div`
  padding: 0;
  display: flex;
  align-items: flex-start;
  flex-flow: column nowrap;
  margin-bottom: 2rem;

  @media (max-width: ${style.collapse}px) {
    background-color: white;
    width: 100%;
    padding: 0 1rem 1.5rem;
    margin-bottom: 0;
    align-items: center;
    display: ${({ hideOnMobile }) => (hideOnMobile ? "none" : "flex")};
  }
`;

const GroupUserActions = (props) => {
  const { isAuthenticated, isMember, isActiveMember, isManager } = props;

  if (!isAuthenticated) {
    return (
      <StyledContent>
        <AnonymousActions />
      </StyledContent>
    );
  }

  if (!isMember) {
    return (
      <StyledContent>
        <NonMemberActions {...props} />
      </StyledContent>
    );
  }

  if (!isActiveMember) {
    return (
      <StyledContent>
        <FollowerActions {...props} />
      </StyledContent>
    );
  }

  if (!isManager) {
    return (
      <StyledContent>
        <MemberActions {...props} />
      </StyledContent>
    );
  }

  return (
    <StyledContent>
      <ManagerActions {...props} />
    </StyledContent>
  );
};

GroupUserActions.propTypes = {
  isAuthenticated: PropTypes.bool,
  isMember: PropTypes.bool,
  isActiveMember: PropTypes.bool,
  isManager: PropTypes.bool,
};

export default GroupUserActions;
