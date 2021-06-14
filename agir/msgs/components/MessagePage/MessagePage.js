import PropTypes from "prop-types";
import React from "react";
import Helmet from "react-helmet";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

import {
  useMessageSWR,
  useSelectMessage,
  useMessageActions,
} from "@agir/msgs/hooks";

import { Hide } from "@agir/front/genericComponents/grid";
import MessageActionModal from "@agir/front/formComponents/MessageActionModal";
import MessageModal from "@agir/front/formComponents/MessageModal/Modal";
import Navigation from "@agir/front/dashboardComponents/Navigation";
import NotificationSettings from "@agir/activity/NotificationSettings/NotificationSettings";
import PageFadeIn from "@agir/front/genericComponents/PageFadeIn";
import Skeleton from "@agir/front/genericComponents/Skeleton";

import MessageThreadList from "./MessageThreadList";
import EmptyMessagePage from "./EmptyMessagePage";

const StyledPageFadeIn = styled(PageFadeIn)``;
const StyledPage = styled.div`
  margin: 0 auto;
  width: 100%;
  max-width: 1320px;
  height: calc(100vh - 84px);
  padding: 2.625rem 1.5rem 1.5rem;

  @media (max-width: ${style.collapse}px) {
    padding: 0;
    height: calc(100vh - 56px);
    max-width: 100%;
  }

  & > ${StyledPageFadeIn} {
    height: 100%;
    width: 100%;
  }
`;

const MessagePage = ({ messagePk }) => {
  const onSelectMessage = useSelectMessage();
  const { user, messages, messageRecipients, currentMessage } = useMessageSWR(
    messagePk,
    onSelectMessage
  );

  const {
    isLoading,
    messageAction,
    selectedGroupEvents,
    writeNewMessage,
    writeNewComment,
    editMessage,
    confirmDelete,
    confirmReport,
    confirmDeleteComment,
    confirmReportComment,
    onDelete,
    onReport,
    dismissMessageAction,
    getSelectedGroupEvents,
    saveMessage,
  } = useMessageActions(
    user,
    messageRecipients,
    currentMessage,
    onSelectMessage
  );

  const shouldShowMessageModal =
    messageAction === "create" || messageAction === "edit";
  const shouldShowMessageActionModal =
    messageAction === "report" || messageAction === "delete";

  return (
    <>
      <Helmet>
        <title>
          {currentMessage?.subject || "Messages"} - Action Populaire
        </title>
      </Helmet>
      <NotificationSettings />
      <StyledPage>
        <StyledPageFadeIn
          ready={user && typeof messages !== "undefined"}
          wait={<Skeleton />}
        >
          {!!writeNewMessage && (
            <MessageModal
              shouldShow={shouldShowMessageModal}
              onClose={dismissMessageAction}
              user={user}
              groups={messageRecipients}
              onSelectGroup={getSelectedGroupEvents}
              events={selectedGroupEvents}
              isLoading={isLoading}
              message={messageAction === "edit" ? currentMessage : null}
              onSend={saveMessage}
            />
          )}
          {currentMessage && (
            <MessageActionModal
              action={shouldShowMessageActionModal ? messageAction : undefined}
              shouldShow={shouldShowMessageActionModal}
              onClose={dismissMessageAction}
              onDelete={onDelete}
              onReport={onReport}
              isLoading={isLoading}
            />
          )}
          {Array.isArray(messages) && messages.length > 0 ? (
            <MessageThreadList
              isLoading={isLoading}
              messages={messages}
              selectedMessagePk={messagePk}
              selectedMessage={currentMessage}
              onSelect={onSelectMessage}
              onEdit={editMessage}
              onDelete={confirmDelete}
              onReport={confirmReport}
              onDeleteComment={confirmDeleteComment}
              onReportComment={confirmReportComment}
              user={user}
              writeNewMessage={writeNewMessage}
              onComment={writeNewComment}
            />
          ) : (
            <EmptyMessagePage />
          )}
        </StyledPageFadeIn>
      </StyledPage>
      <Hide over>
        <Navigation active="messages" />
      </Hide>
    </>
  );
};

MessagePage.propTypes = {
  messagePk: PropTypes.string,
};

export default MessagePage;
