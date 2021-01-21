import PropTypes from "prop-types";
import React from "react";

import GroupMessages from "@agir/groups/groupPage/GroupMessages";

const MessagesRoute = ({
  user,
  allEvents,
  messages,
  getMessageURL,
  isLoadingMessages,
  loadMoreMessages,
  loadMorePastEvents,
  createMessage,
  updateMessage,
  createComment,
  reportMessage,
  deleteMessage,
  onClickMessage,
}) => (
  <GroupMessages
    user={user}
    events={allEvents}
    messages={messages}
    getMessageURL={getMessageURL}
    isLoading={isLoadingMessages}
    onClick={onClickMessage}
    loadMoreMessages={loadMoreMessages}
    loadMoreEvents={loadMorePastEvents}
    createMessage={createMessage}
    updateMessage={updateMessage}
    createComment={createComment}
    reportMessage={reportMessage}
    deleteMessage={deleteMessage}
  />
);
MessagesRoute.propTypes = {
  allEvents: PropTypes.arrayOf(PropTypes.object),
  loadMorePastEvents: PropTypes.func,
  message: PropTypes.object,
  messages: PropTypes.arrayOf(PropTypes.object),
  isLoadingMessages: PropTypes.bool,
  loadMoreMessages: PropTypes.func,
  createMessage: PropTypes.func,
  updateMessage: PropTypes.func,
  createComment: PropTypes.func,
  reportMessage: PropTypes.func,
  deleteMessage: PropTypes.func,
  onClickMessage: PropTypes.func,
  user: PropTypes.object,
  getMessageURL: PropTypes.func,
};

export default MessagesRoute;
