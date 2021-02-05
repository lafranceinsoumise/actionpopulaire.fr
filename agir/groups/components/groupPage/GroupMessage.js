import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

import MessageCard from "@agir/front/genericComponents/MessageCard";
import PageFadeIn from "@agir/front/genericComponents/PageFadeIn";
import Skeleton from "@agir/front/genericComponents/Skeleton";

import MessageModal from "@agir/front/formComponents/MessageModal/Modal";
import MessageActionModal from "@agir/front/formComponents/MessageActionModal";

import { useMessageActions } from "@agir/groups/groupPage/hooks";

const StyledMessage = styled.div``;
const StyledWrapper = styled.div`
  @media (max-width: ${style.collapse}px) {
    padding-bottom: 2.5rem;
  }
`;

const GroupMessage = (props) => {
  const {
    user,
    message,
    events,
    isManager,
    isLoading,
    messageURL,
    groupURL,
    onClick,
    loadMoreEvents,
  } = props;

  const {
    selectedMessage,
    messageAction,
    writeNewComment,
    editMessage,
    confirmDelete,
    confirmReport,
    dismissMessageAction,
    saveMessage,
    handleDelete,
    handleReport,
  } = useMessageActions(props);

  const hasMessageModal =
    messageAction === "edit" || messageAction === "create";
  const hasMessageActionModal =
    messageAction === "delete" || messageAction === "report";

  return (
    <StyledWrapper>
      {saveMessage ? (
        <MessageModal
          shouldShow={hasMessageModal}
          onClose={dismissMessageAction}
          user={user}
          events={events}
          loadMoreEvents={loadMoreEvents}
          isLoading={isLoading}
          message={selectedMessage}
          onSend={saveMessage}
        />
      ) : null}
      <MessageActionModal
        action={hasMessageActionModal ? messageAction : undefined}
        shouldShow={hasMessageActionModal}
        onClose={dismissMessageAction}
        onReport={handleReport}
        onDelete={handleDelete}
        isLoading={isLoading}
      />
      <PageFadeIn
        ready={message !== undefined}
        wait={<Skeleton style={{ margin: "1rem 0" }} />}
      >
        <StyledMessage>
          {message && (
            <MessageCard
              message={message}
              user={user}
              comments={message.comments}
              onClick={onClick}
              onEdit={editMessage}
              onComment={writeNewComment}
              onReport={confirmReport}
              onDelete={confirmDelete}
              messageURL={messageURL}
              isManager={isManager}
              groupURL={groupURL}
              withMobileCommentField
            />
          )}
        </StyledMessage>
      </PageFadeIn>
    </StyledWrapper>
  );
};
GroupMessage.propTypes = {
  user: PropTypes.object,
  events: PropTypes.arrayOf(PropTypes.object),
  message: PropTypes.object,
  isLoading: PropTypes.bool,
  isManager: PropTypes.bool,
  messageURL: PropTypes.string,
  groupURL: PropTypes.string,
  onClick: PropTypes.func,
  createMessage: PropTypes.func,
  updateMessage: PropTypes.func,
  createComment: PropTypes.func,
  reportMessage: PropTypes.func,
  deleteMessage: PropTypes.func,
  loadMoreEvents: PropTypes.func,
  loadMoreMessages: PropTypes.func,
};
export default GroupMessage;
