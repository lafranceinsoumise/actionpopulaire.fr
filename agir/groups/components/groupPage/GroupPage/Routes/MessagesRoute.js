import PropTypes from "prop-types";
import React from "react";

import GroupMessages from "@agir/groups/groupPage/GroupMessages";

const MessagesRoute = ({
  allEvents,
  isLoadingMessages,
  loadMorePastEvents,
  onClickMessage,
  ...rest
}) => (
  <GroupMessages
    {...rest}
    events={allEvents}
    isLoading={isLoadingMessages}
    onClick={onClickMessage}
    loadMoreEvents={loadMorePastEvents}
  />
);
MessagesRoute.propTypes = {
  allEvents: PropTypes.arrayOf(PropTypes.object),
  isLoadingMessages: PropTypes.bool,
  loadMorePastEvents: PropTypes.func,
  onClickMessage: PropTypes.func,
};

export default MessagesRoute;
