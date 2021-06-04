import PropTypes from "prop-types";
import React, {
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";
import Helmet from "react-helmet";
import { useHistory } from "react-router-dom";
import styled from "styled-components";
import useSWR, { mutate } from "swr";

import style from "@agir/front/genericComponents/_variables.scss";

import { Hide } from "@agir/front/genericComponents/grid";
import MessageActionModal from "@agir/front/formComponents/MessageActionModal";
import MessageModal from "@agir/front/formComponents/MessageModal/Modal";
import Navigation from "@agir/front/dashboardComponents/Navigation";
import PageFadeIn from "@agir/front/genericComponents/PageFadeIn";
import Skeleton from "@agir/front/genericComponents/Skeleton";

import MessageThreadList from "./MessageThreadList";
import EmptyMessagePage from "./EmptyMessagePage";

import axios from "@agir/lib/utils/axios";
import * as groupAPI from "@agir/groups/groupPage/api";
import { routeConfig } from "@agir/front/app/routes.config";
import { setBackLink } from "@agir/front/globalContext/actions";
import { useDispatch } from "@agir/front/globalContext/GlobalContext";

const StyledPage = styled.div`
  margin: 0 auto;
  width: 100%;
  max-width: 1320px;
  height: calc(100vh - 84px);
  padding: 2.625rem 1.5rem;

  @media (max-width: ${style.collapse}px) {
    padding: 0;
    height: auto;
    max-width: 100%;
  }
`;

const useMessageSWR = (messagePk) => {
  const dispatch = useDispatch();
  const { data: session } = useSWR("/api/session");
  const { data: messages } = useSWR("/api/user/messages/", {
    refreshInterval: 1000,
  });
  const { data: messageRecipients } = useSWR("/api/user/messages/recipients/");
  const { data: currentMessage } = useSWR(
    messagePk ? `/api/groupes/messages/${messagePk}/` : null
  );

  const currentMessageId = currentMessage?.id;
  useEffect(() => {
    dispatch(
      setBackLink(
        currentMessageId
          ? {
              route: "messages",
              label: "Retour aux messages",
            }
          : {
              route: "events",
              label: "Retour à l'accueil",
            }
      )
    );
  }, [dispatch, currentMessageId]);

  return {
    user: session?.user,
    messages,
    messageRecipients,
    currentMessage,
  };
};

const useSelectMessage = () => {
  const history = useHistory();
  const handleSelect = useCallback(
    (messagePk, doNotPush = false) => {
      if (doNotPush) {
        history.replace(routeConfig.messages.getLink({ messagePk }));
      } else {
        history.push(routeConfig.messages.getLink({ messagePk }));
      }
    },
    [history]
  );

  return handleSelect;
};

const useMessageActions = (
  user,
  messageRecipients,
  selectedMessage,
  onSelectMessage
) => {
  const shouldDismissAction = useRef(false);

  const [isLoading, setIsLoading] = useState(false);

  const [selectedGroupEvents, setSelectedGroupEvents] = useState([]);
  const [selectedComment, setSelectedComment] = useState(null);

  const [messageAction, setMessageAction] = useState("");

  const canWriteNewMessage = useMemo(
    () =>
      !!user &&
      Array.isArray(messageRecipients) &&
      messageRecipients.length > 0,
    [user, messageRecipients]
  );

  const canEditSelectedMessage = useMemo(
    () =>
      canWriteNewMessage &&
      selectedMessage?.group &&
      messageRecipients.some((r) => r.id === selectedMessage.group.id),
    [canWriteNewMessage, messageRecipients, selectedMessage]
  );

  const isAuthor = useMemo(() => {
    if (!selectedMessage && !selectedComment) {
      return false;
    }
    if (selectedComment) {
      return user && selectedComment && selectedComment.author.id === user.id;
    }
    return user && selectedMessage && selectedMessage.author.id === user.id;
  }, [user, selectedMessage, selectedComment]);

  const getSelectedGroupEvents = useCallback(async (group) => {
    shouldDismissAction.current = false;
    setIsLoading(true);
    setSelectedGroupEvents([]);
    try {
      const { data: events } = await axios.get(
        `/api/groupes/${group.id}/evenements/`
      );
      setIsLoading(false);
      setSelectedGroupEvents(events);
    } catch (e) {
      setIsLoading(false);
    }
  }, []);

  const saveMessage = useCallback(
    async (message) => {
      setIsLoading(true);
      shouldDismissAction.current = true;
      try {
        const result = message.id
          ? await groupAPI.updateMessage(message)
          : await groupAPI.createMessage(message.group.id, message);
        setIsLoading(false);
        mutate("/api/user/messages/");
        if (message.id) {
          mutate(`/api/groupes/messages/${message.id}/`, () => result.data);
        } else {
          onSelectMessage(result.data.id);
        }
      } catch (e) {
        setIsLoading(false);
      }
    },
    [onSelectMessage]
  );

  const writeNewComment = useCallback(
    async (comment) => {
      setIsLoading(true);
      try {
        const response = await groupAPI.createComment(
          selectedMessage.id,
          comment
        );
        setIsLoading(false);
        mutate(`/api/groupes/messages/${selectedMessage.id}/`, (message) => ({
          ...message,
          comments: Array.isArray(message.comments)
            ? [...message.comments, response.data]
            : [response.data],
        }));
        onSelectMessage(selectedMessage.id);
      } catch (e) {
        setIsLoading(false);
      }
    },
    [selectedMessage, onSelectMessage]
  );

  const onDelete = useCallback(async () => {
    if (!selectedMessage && !selectedComment) {
      return;
    }
    setIsLoading(true);
    try {
      selectedComment
        ? await groupAPI.deleteComment(selectedComment, selectedMessage)
        : await groupAPI.deleteMessage(selectedMessage);
      setIsLoading(false);
    } catch (e) {
      setIsLoading(false);
    }
  }, [selectedMessage, selectedComment]);

  const onReport = useCallback(async () => {
    if (!selectedMessage && !selectedComment) {
      return;
    }
    setIsLoading(true);
    try {
      selectedComment
        ? await groupAPI.reportComment(selectedComment)
        : await groupAPI.reportMessage(selectedMessage);
      setIsLoading(false);
    } catch (e) {
      setIsLoading(false);
    }
  }, [selectedMessage, selectedComment]);

  const writeNewMessage = useCallback(() => {
    setMessageAction("create");
  }, []);

  const editMessage = useCallback(() => {
    getSelectedGroupEvents(selectedMessage.group);
    setMessageAction("edit");
  }, [getSelectedGroupEvents, selectedMessage]);

  const confirmDelete = useCallback(() => {
    setMessageAction("delete");
  }, []);

  const confirmReport = useCallback(() => {
    setMessageAction("report");
  }, []);

  const confirmReportComment = useCallback((comment) => {
    setSelectedComment(comment);
    setMessageAction("report");
  }, []);

  const confirmDeleteComment = useCallback((comment) => {
    setSelectedComment(comment);
    setMessageAction("delete");
  }, []);

  const dismissMessageAction = useCallback(() => {
    if (messageAction === "delete" && selectedMessage && selectedComment) {
      mutate(`/api/groupes/messages/${selectedMessage.id}/`);
    } else if (messageAction === "delete") {
      mutate(`/api/user/messages/`);
      onSelectMessage(null);
    }
    setMessageAction("");
    setSelectedComment(null);
    shouldDismissAction.current = false;
  }, [messageAction, selectedComment, selectedMessage, onSelectMessage]);

  useEffect(() => {
    !isLoading && shouldDismissAction.current && dismissMessageAction();
  }, [isLoading, dismissMessageAction]);

  return {
    isLoading,

    messageAction,
    selectedGroupEvents,
    selectedComment,

    writeNewMessage: canWriteNewMessage ? writeNewMessage : undefined,
    writeNewComment,
    editMessage: canEditSelectedMessage ? editMessage : undefined,
    confirmDelete: canEditSelectedMessage ? confirmDelete : undefined,
    confirmReport,
    confirmDeleteComment,
    confirmReportComment,

    getSelectedGroupEvents,
    saveMessage,
    onDelete:
      messageAction === "delete" || canEditSelectedMessage
        ? onDelete
        : undefined,
    onReport:
      messageAction === "report" || (canEditSelectedMessage && !isAuthor)
        ? onReport
        : undefined,
    dismissMessageAction,
  };
};

const MessagePage = ({ messagePk }) => {
  const { user, messages, messageRecipients, currentMessage } =
    useMessageSWR(messagePk);

  const onSelectMessage = useSelectMessage();

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
        <title>Messages - Action Populaire</title>
      </Helmet>
      <PageFadeIn
        ready={user && typeof messages !== "undefined"}
        wait={
          <StyledPage>
            <Skeleton />
          </StyledPage>
        }
      >
        <StyledPage>
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
        </StyledPage>
      </PageFadeIn>
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
