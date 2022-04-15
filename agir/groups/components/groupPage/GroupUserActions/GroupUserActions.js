import PropTypes from "prop-types";
import React from "react";

import AnonymousActions from "./AnonymousActions";
import NonMemberActions from "./NonMemberActions";
import FollowerActions from "./FollowerActions";
import MemberActions from "./MemberActions";
import ManagerActions from "./ManagerActions";

const GroupUserActions = (props) => {
  const { isAuthenticated, isMember, isActiveMember, isManager } = props;

  if (!isAuthenticated) {
    return <AnonymousActions {...props} />;
  }

  if (!isMember) {
    return <NonMemberActions {...props} />;
  }

  if (!isActiveMember) {
    return <FollowerActions {...props} />;
  }

  if (!isManager) {
    return <MemberActions {...props} />;
  }

  return <ManagerActions {...props} />;
};

GroupUserActions.propTypes = {
  isAuthenticated: PropTypes.bool,
  isMember: PropTypes.bool,
  isActiveMember: PropTypes.bool,
  isManager: PropTypes.bool,
};

export default GroupUserActions;
