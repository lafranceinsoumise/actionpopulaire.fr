import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

import Button from "@agir/front/genericComponents/Button";
import MessageCard from "@agir/front/genericComponents/MessageCard";
import PageFadeIn from "@agir/front/genericComponents/PageFadeIn";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";
import Skeleton from "@agir/front/genericComponents/Skeleton";

import MessageModalTrigger from "@agir/front/formComponents/MessageModal/Trigger";
import MessageModal from "@agir/front/formComponents/MessageModal/Modal";
import MessageActionModal from "@agir/front/formComponents/MessageActionModal";

import { EmptyMessages } from "./EmptyContent";

import { useMessageActions } from "@agir/groups/groupPage/hooks";

const StyledButton = styled.div`
  text-align: center;

  @media (max-width: ${style.collapse}px) {
    box-shadow: ${style.elaborateShadow} inset;
  }

  ${Button} {
    width: auto;
    margin: 0 auto;
    justify-content: center;

    &,
    &:hover,
    &:focus,
    &:active {
      background-color: white;
    }

    @media (max-width: ${style.collapse}px) {
      width: 100%;
      margin-top: 1rem;
      font-size: 0.875rem;
      box-shadow: ${style.elaborateShadow};
    }
  }
`;
const StyledMessages = styled.div`
  margin-top: 1rem;

  @media (max-width: ${style.collapse}px) {
    background-color: ${style.black50};
  }
`;
const StyledWrapper = styled.div`
  @media (max-width: ${style.collapse}px) {
    margin-top: 1rem;
  }
`;

const GroupMessages = (props) => {
  const {
    user,
    messages,
    events,
    isManager,
    isLoading,
    getMessageURL,
    onClick,
    loadMoreEvents,
    loadMoreMessages,
  } = props;

  const {
    selectedMessage,
    messageAction,
    writeNewMessage,
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
      {Array.isArray(messages) && messages.length > 0 && writeNewMessage ? (
        <div style={{ border: `1px solid ${style.black50}` }}>
          <MessageModalTrigger onClick={writeNewMessage} />
        </div>
      ) : null}
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
        ready={Array.isArray(messages)}
        wait={<Skeleton style={{ margin: "1rem 0" }} />}
      >
        <StyledMessages>
          {Array.isArray(messages) && messages.length > 0
            ? messages.map((message) => (
                <MessageCard
                  key={message.id}
                  message={message}
                  user={user}
                  comments={message.recentComments}
                  onClick={onClick}
                  onEdit={editMessage}
                  onComment={writeNewComment}
                  onReport={confirmReport}
                  onDelete={confirmDelete}
                  messageURL={getMessageURL && getMessageURL(message.id)}
                  isManager={isManager}
                />
              ))
            : null}
          {Array.isArray(messages) && messages.length === 0 ? (
            <EmptyMessages onClickSendMessage={writeNewMessage} />
          ) : null}
          {typeof loadMoreMessages === "function" ? (
            <StyledButton>
              <Button
                color="white"
                onClick={loadMoreMessages}
                disabled={isLoading}
              >
                Charger plus d'actualités&ensp;
                <RawFeatherIcon
                  name="chevron-down"
                  width="1em"
                  strokeWidth={3}
                />
              </Button>
            </StyledButton>
          ) : null}
        </StyledMessages>
      </PageFadeIn>
    </StyledWrapper>
  );
};
GroupMessages.propTypes = {
  user: PropTypes.object,
  events: PropTypes.arrayOf(PropTypes.object),
  messages: PropTypes.arrayOf(PropTypes.object),
  isLoading: PropTypes.bool,
  isManager: PropTypes.bool,
  getMessageURL: PropTypes.func,
  onClick: PropTypes.func,
  createMessage: PropTypes.func,
  updateMessage: PropTypes.func,
  createComment: PropTypes.func,
  reportMessage: PropTypes.func,
  deleteMessage: PropTypes.func,
  loadMoreEvents: PropTypes.func,
  loadMoreMessages: PropTypes.func,
};
export default GroupMessages;
