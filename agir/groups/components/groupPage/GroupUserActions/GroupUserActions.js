import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

import AnonymousActions from "./AnonymousActions";
import NonMemberActions from "./NonMemberActions";
import FollowerActions from "./FollowerActions";
import MemberActions from "./MemberActions";
import ManagerActions from "./ManagerActions";

import SecondaryActions from "./SecondaryActions";

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
  const { isAuthenticated, isMember, isActiveMember, isManager, routes } =
    props;

  const isNonMemberActions = !isAuthenticated && !isMember;
  const isFollowerActions = !isNonMemberActions && !isActiveMember;
  const isMemberActions = !isFollowerActions && !isManager;

  return (
    <StyledContent>
      {!isAuthenticated && <AnonymousActions {...props} />}
      {isNonMemberActions && <NonMemberActions {...props} />}
      {isFollowerActions && <FollowerActions {...props} />}
      {isMemberActions && <MemberActions {...props} />}
      {!isMemberActions && <ManagerActions {...props} />}
      <SecondaryActions routes={routes} />
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
