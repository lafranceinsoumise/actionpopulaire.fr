import PropTypes from "prop-types";
import React, { useEffect } from "react";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

import {
  useMessageSWR,
  useSelectMessage,
  useMessageActions,
} from "@agir/msgs/common/hooks";
import { useDispatch } from "@agir/front/globalContext/GlobalContext";
import { setPageTitle } from "@agir/front/globalContext/actions";
import { getMessageSubject } from "@agir/msgs/common/utils";
import { useIsOffline } from "@agir/front/offline/hooks";

import { Hide } from "@agir/front/genericComponents/grid";
import MessageActionModal from "@agir/front/formComponents/MessageActionModal";
import MessageModal from "@agir/front/formComponents/MessageModal/Modal";
import BottomBar from "@agir/front/app/Navigation/BottomBar";
import NotificationSettings from "@agir/notifications/NotificationSettings/NotificationSettings";
import OpenGraphTags from "@agir/front/app/OpenGraphTags";
import PageFadeIn from "@agir/front/genericComponents/PageFadeIn";
import Skeleton from "@agir/front/genericComponents/Skeleton";
import NotFoundPage from "@agir/front/notFoundPage/NotFoundPage";

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
  const isOffline = useIsOffline();
  const dispatch = useDispatch();
  const onSelectMessage = useSelectMessage();
  const {
    user,
    messages,
    messageRecipients,
    currentMessage,
    isAutoRefreshPausedRef,
  } = useMessageSWR(messagePk, onSelectMessage);

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

  // Pause messages' autorefresh while an action is ongoing
  isAutoRefreshPausedRef.current = isLoading || !!messageAction;

  const shouldShowMessageModal =
    messageAction === "create" || messageAction === "edit";
  const shouldShowMessageActionModal =
    messageAction === "report" || messageAction === "delete";

  const pageTitle = currentMessage
    ? getMessageSubject(currentMessage)
    : "Messages";

  useEffect(() => {
    dispatch(setPageTitle(pageTitle));
  }, [dispatch, pageTitle]);

  return (
    <>
      <OpenGraphTags title={pageTitle} />
      <NotificationSettings />
      <StyledPage>
        {!isOffline || !messages ? (
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
                action={
                  shouldShowMessageActionModal ? messageAction : undefined
                }
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
        ) : (
          <NotFoundPage isTopBar={false} reloadOnReconnection={false} />
        )}
      </StyledPage>
      <Hide over>
        <BottomBar active="messages" />
      </Hide>
    </>
  );
};

MessagePage.propTypes = {
  messagePk: PropTypes.string,
};

export default MessagePage;
