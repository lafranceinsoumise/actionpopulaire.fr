import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

import { withMessageActions } from "@agir/groups/groupPage/hooks/messages";

import MessageCard from "@agir/front/genericComponents/MessageCard";
import PageFadeIn from "@agir/front/genericComponents/PageFadeIn";
import Skeleton from "@agir/front/genericComponents/Skeleton";

import MessageModal from "@agir/front/formComponents/MessageModal/Modal";
import MessageActionModal from "@agir/front/formComponents/MessageActionModal";

const StyledMessage = styled.div``;
const StyledWrapper = styled.div`
  @media (max-width: ${style.collapse}px) {
    padding-bottom: 2.5rem;
  }
`;

export const GroupMessage = (props) => {
  const {
    group,
    user,
    message,
    selectedMessage,
    events,
    messageAction,
    messageURL,
    groupURL,
    isLoading,
    isUpdating,
    hasMessageModal,
    hasMessageActionModal,
    loadMoreEvents,
    onClick,
    editMessage,
    confirmReport,
    confirmDelete,
    writeNewComment,
    confirmReportComment,
    confirmDeleteComment,
    dismissMessageAction,
    saveMessage,
    onDelete,
    onReport,
  } = props;

  const isManager = group && group.isManager;

  return (
    <StyledWrapper>
      {saveMessage ? (
        <MessageModal
          shouldShow={hasMessageModal}
          onClose={dismissMessageAction}
          user={user}
          events={events}
          loadMoreEvents={loadMoreEvents}
          isLoading={isUpdating}
          message={selectedMessage}
          onSend={saveMessage}
        />
      ) : null}
      <MessageActionModal
        action={hasMessageActionModal ? messageAction : undefined}
        shouldShow={hasMessageActionModal}
        onClose={dismissMessageAction}
        onReport={onReport}
        onDelete={onDelete}
        isLoading={isUpdating}
      />
      <PageFadeIn
        ready={!isLoading}
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
              onReportComment={confirmReportComment}
              onDeleteComment={confirmDeleteComment}
              messageURL={messageURL}
              isManager={isManager}
              groupURL={groupURL}
              isLoading={isUpdating}
              withMobileCommentField
            />
          )}
        </StyledMessage>
      </PageFadeIn>
    </StyledWrapper>
  );
};
GroupMessage.propTypes = {
  group: PropTypes.shape({
    isManager: PropTypes.bool,
  }),
  user: PropTypes.object,
  message: PropTypes.object,
  selectedMessage: PropTypes.object,
  events: PropTypes.arrayOf(PropTypes.object),
  messageAction: PropTypes.string,
  messageURL: PropTypes.string,
  groupURL: PropTypes.string,
  isLoading: PropTypes.bool,
  isUpdating: PropTypes.bool,
  isManager: PropTypes.bool,
  hasMessageModal: PropTypes.bool,
  hasMessageActionModal: PropTypes.bool,
  loadMoreEvents: PropTypes.func,
  onClick: PropTypes.func,
  editMessage: PropTypes.func,
  confirmReport: PropTypes.func,
  confirmDelete: PropTypes.func,
  writeNewComment: PropTypes.func,
  confirmReportComment: PropTypes.func,
  confirmDeleteComment: PropTypes.func,
  dismissMessageAction: PropTypes.func,
  saveMessage: PropTypes.func,
  onDelete: PropTypes.func,
  onReport: PropTypes.func,
};

const ConnectedGroupMessage = withMessageActions(GroupMessage);

export default ConnectedGroupMessage;
