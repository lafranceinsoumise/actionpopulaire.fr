import PropTypes from "prop-types";
import React from "react";

import { useUnreadMessageCount } from "@agir/msgs/common/hooks";
import { useUnreadActivityCount } from "@agir/activity/common/hooks";

import BottomBar from "./BottomBar";

const ConnectedBottomBar = (props) => {
  const unreadActivityCount = useUnreadActivityCount();
  const unreadMessageCount = useUnreadMessageCount();

  return (
    <BottomBar
      {...props}
      unreadActivityCount={unreadActivityCount}
      unreadMessageCount={unreadMessageCount}
    />
  );
};

export default ConnectedBottomBar;
