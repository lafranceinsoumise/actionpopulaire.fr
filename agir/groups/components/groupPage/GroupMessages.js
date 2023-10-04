import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

import { withMessageActions } from "@agir/groups/groupPage/hooks/messages";

import Button from "@agir/front/genericComponents/Button";
import Spacer from "@agir/front/genericComponents/Spacer";
import MessageCard from "@agir/front/genericComponents/MessageCard";
import PageFadeIn from "@agir/front/genericComponents/PageFadeIn";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";
import Skeleton from "@agir/front/genericComponents/Skeleton";
import { ResponsiveLayout } from "@agir/front/genericComponents/grid";

import MessageModalTrigger, {
  FloatingTrigger as FloatingMessageModalTrigger,
} from "@agir/front/formComponents/MessageModal/Trigger";
import MessageModal from "@agir/front/formComponents/MessageModal/Modal";
import MessageActionModal from "@agir/front/formComponents/MessageActionModal";
import { PromoMessage } from "@agir/groups/messages/PromoMessageModal";

const StyledButton = styled.div`
  text-align: center;

  @media (max-width: ${style.collapse}px) {
    box-shadow: ${style.elaborateShadow} inset;
  }

  ${Button} {
    &,
    &:hover,
    &:focus,
    &:active {
      background-color: white;
      width: auto;
      margin: 0 auto;
      justify-content: center;

      @media (max-width: ${style.collapse}px) {
        width: 100%;
        margin-top: 1rem;
        font-size: 0.875rem;
        box-shadow: ${style.elaborateShadow};
      }
    }
  }
`;
const StyledMessages = styled.div`
  margin-top: 1rem;
  display: flex;
  justify-content: center;
  align-items: center;
  flex-direction: column;

  @media (max-width: ${style.collapse}px) {
    background-color: ${style.black50};
  }
`;
const StyledWrapper = styled.div`
  @media (max-width: ${style.collapse}px) {
    margin-top: 1rem;
  }

  & > h3 {
    margin: 0;
    padding: 0 0 1.5rem 0;

    @media (max-width: ${style.collapse}px) {
      padding: 1.5rem 1rem 0.5rem;
    }
  }
`;

export const GroupMessages = (props) => {
  const {
    user,
    group,
    events,
    messages,
    selectedMessage,
    messageAction,
    isLoading,
    isUpdating,
    hasMessageModal,
    hasMessageActionModal,
    getMessageURL,
    onClick,
    loadMoreEvents,
    loadMoreMessages,
    writeNewMessage,
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
      <h3>
        <PageFadeIn
          ready={!isLoading && Array.isArray(messages)}
          wait={
            <Skeleton
              boxes={1}
              style={{ width: "50%", height: "2em", margin: 0 }}
            />
          }
        >
          Messages
        </PageFadeIn>
      </h3>
      {Array.isArray(messages) && writeNewMessage ? (
        <ResponsiveLayout
          MobileLayout={FloatingMessageModalTrigger}
          DesktopLayout={MessageModalTrigger}
          onClick={writeNewMessage}
          outlined
        />
      ) : null}
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
        ready={!isLoading && Array.isArray(messages)}
        wait={<Skeleton style={{ margin: "1rem 0" }} />}
      >
        <StyledMessages>
          {Array.isArray(messages) && messages.length > 0
            ? messages.map((message) => (
                <>
                  <MessageCard
                    key={message.id}
                    message={message}
                    user={user}
                    comments={message.comments || message.recentComments}
                    onClick={onClick}
                    onEdit={editMessage}
                    onComment={writeNewComment}
                    onReport={confirmReport}
                    onDelete={confirmDelete}
                    onDeleteComment={confirmDeleteComment}
                    onReportComment={confirmReportComment}
                    messageURL={getMessageURL && getMessageURL(message.id)}
                    isManager={isManager}
                    isLoading={isUpdating}
                  />
                  <Spacer size="1rem" />
                </>
              ))
            : null}

          {isManager && !isLoading && !messages?.length && (
            <PromoMessage onClick={writeNewMessage} />
          )}

          {typeof loadMoreMessages === "function" ? (
            <StyledButton>
              <Button
                color="white"
                onClick={loadMoreMessages}
                disabled={isLoading}
                icon="chevron-down"
                rightIcon
              >
                Charger plus de messages
              </Button>
            </StyledButton>
          ) : null}
        </StyledMessages>
      </PageFadeIn>
    </StyledWrapper>
  );
};
GroupMessages.propTypes = {
  group: PropTypes.shape({
    isManager: PropTypes.bool,
  }),
  user: PropTypes.object,
  events: PropTypes.arrayOf(PropTypes.object),
  messages: PropTypes.arrayOf(PropTypes.object),
  selectedMessage: PropTypes.object,
  messageAction: PropTypes.string,
  isLoading: PropTypes.bool,
  isUpdating: PropTypes.bool,
  isManager: PropTypes.bool,
  hasMessageModal: PropTypes.bool,
  hasMessageActionModal: PropTypes.bool,
  getMessageURL: PropTypes.func,
  onClick: PropTypes.func,
  loadMoreEvents: PropTypes.func,
  loadMoreMessages: PropTypes.func,
  writeNewMessage: PropTypes.func,
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

const ConnectedGroupMessages = withMessageActions(GroupMessages);

export default ConnectedGroupMessages;
