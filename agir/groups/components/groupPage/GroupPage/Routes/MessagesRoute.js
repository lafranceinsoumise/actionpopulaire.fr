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
  reportMessage,
  deleteMessage,
  onClickMessage,
  createComment,
  reportComment,
  deleteComment,
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
    reportMessage={reportMessage}
    deleteMessage={deleteMessage}
    createComment={createComment}
    reportComment={reportComment}
    deleteComment={deleteComment}
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
  reportMessage: PropTypes.func,
  deleteMessage: PropTypes.func,
  onClickMessage: PropTypes.func,
  createComment: PropTypes.func,
  reportComment: PropTypes.func,
  deleteComment: PropTypes.func,
  user: PropTypes.object,
  getMessageURL: PropTypes.func,
};

export default MessagesRoute;
