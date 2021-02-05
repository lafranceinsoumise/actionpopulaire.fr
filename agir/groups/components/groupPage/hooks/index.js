import { useCallback, useEffect, useMemo, useRef, useState } from "react";

import { useGroup, useGroupSuggestions } from "./group";
import {
  useUpcomingEvents,
  usePastEvents,
  usePastEventReports,
} from "./events";
import { useMessages, useMessage } from "./messages";

export const useGroupDetail = (groupPk) => {
  const group = useGroup(groupPk);
  const groupSuggestions = useGroupSuggestions(group);
  const upcomingEvents = useUpcomingEvents(group);
  const {
    pastEvents,
    pastEventCount,
    isLoadingPastEvents,
    loadMorePastEvents,
  } = usePastEvents(group);
  const pastEventReports = usePastEventReports(group);
  const {
    messages,
    isLoadingMessages,
    loadMoreMessages,
    createMessage,
    updateMessage,
    reportMessage,
    deleteMessage,
    createComment,
    deleteComment,
    reportComment,
  } = useMessages(group);

  const allEvents = useMemo(
    () => [...(upcomingEvents || []), ...(pastEvents || [])],
    [upcomingEvents, pastEvents]
  );

  return {
    group: group,
    groupSuggestions,
    allEvents,
    upcomingEvents,
    pastEvents,
    pastEventCount,
    loadMorePastEvents,
    isLoadingPastEvents,
    pastEventReports,
    messages,
    loadMoreMessages,
    isLoadingMessages,
    createMessage,
    updateMessage,
    reportMessage,
    deleteMessage,
    createComment,
    deleteComment,
    reportComment,
  };
};

export const useGroupMessage = (groupPk, messagePk) => {
  const group = useGroup(groupPk);
  const upcomingEvents = useUpcomingEvents(
    group && group.isMember ? group : null
  );
  const { pastEvents, loadMorePastEvents: loadMoreEvents } = usePastEvents(
    group && group.isMember ? group : null
  );

  const {
    message,
    isLoading,
    updateMessage,
    deleteMessage,
    createComment,
    deleteComment,
  } = useMessage(group, messagePk);

  const events = useMemo(
    () => [...(upcomingEvents || []), ...(pastEvents || [])],
    [upcomingEvents, pastEvents]
  );

  return {
    group,
    message,
    events,
    loadMoreEvents,
    updateMessage,
    // reportMessage,
    deleteMessage,
    createComment,
    deleteComment,
    // reportComment,
    isLoading,
  };
};

export const useMessageActions = (props) => {
  const {
    user,
    isManager,
    isLoading,
    createMessage,
    updateMessage,
    createComment,
    reportMessage,
    reportComment,
    deleteMessage,
    deleteComment,
  } = props;

  const shouldDismiss = useRef(false);

  const [selectedMessage, setSelectedMessage] = useState(null);
  const [selectedComment, setSelectedComment] = useState(null);

  const [messageAction, setMessageAction] = useState("");

  const writeNewMessage = useCallback(() => {
    setMessageAction("create");
  }, []);
  const editMessage = useCallback((message) => {
    setSelectedMessage(message);
    setMessageAction("edit");
  }, []);
  const confirmReport = useCallback((message) => {
    setSelectedMessage(message);
    setMessageAction("report");
  }, []);
  const confirmDelete = useCallback((message) => {
    setSelectedMessage(message);
    setMessageAction("delete");
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
    setMessageAction("");
    setSelectedMessage(null);
    setSelectedComment(null);
    shouldDismiss.current = false;
  }, []);

  const saveMessage = useCallback(
    (message) => {
      if (message.id && updateMessage) {
        shouldDismiss.current = true;
        updateMessage(message);
      } else if (createMessage) {
        shouldDismiss.current = true;
        createMessage(message);
      }
    },
    [createMessage, updateMessage]
  );

  const handleDelete = useCallback(() => {
    if (!selectedMessage && !selectedComment) {
      return;
    }
    if (selectedMessage && deleteMessage) {
      shouldDismiss.current = true;
      deleteMessage(selectedMessage);
    }
    if (selectedComment && deleteComment) {
      shouldDismiss.current = true;
      deleteComment(selectedComment);
    }
  }, [selectedMessage, selectedComment, deleteMessage, deleteComment]);

  const handleReport = useCallback(() => {
    if (!selectedMessage && !selectedComment) {
      return;
    }
    if (selectedMessage && reportMessage) {
      shouldDismiss.current = true;
      reportMessage(selectedMessage);
    }
    if (selectedComment && reportComment) {
      shouldDismiss.current = true;
      reportComment(selectedComment);
    }
  }, [selectedMessage, selectedComment, reportMessage, reportComment]);

  useEffect(() => {
    !isLoading && shouldDismiss.current && dismissMessageAction();
  }, [isLoading, dismissMessageAction]);

  const isAuthor = useMemo(() => {
    const isSelectedMessageAuthor =
      user && selectedMessage && selectedMessage.author.id === user.id;
    const isSelectedCommentAuthor =
      user && selectedComment && selectedComment.author.id === user.id;
    return isSelectedMessageAuthor || isSelectedCommentAuthor;
  }, [user, selectedMessage, selectedComment]);

  return {
    selectedMessage: selectedMessage || selectedComment || null,

    messageAction,
    dismissMessageAction,

    writeNewMessage: createMessage ? writeNewMessage : undefined,
    editMessage: updateMessage ? editMessage : undefined,
    confirmDelete: deleteMessage ? confirmDelete : undefined,
    confirmReport: reportMessage ? confirmReport : undefined,

    writeNewComment: createComment || undefined,
    confirmDeleteComment: deleteComment ? confirmDeleteComment : undefined,
    confirmReportComment: reportComment ? confirmReportComment : undefined,

    saveMessage: createMessage || updateMessage ? saveMessage : undefined,

    handleDelete:
      messageAction === "delete" || (isManager && !isAuthor)
        ? handleDelete
        : undefined,

    handleReport:
      messageAction === "report" || (isManager && !isAuthor)
        ? handleReport
        : undefined,
  };
};
