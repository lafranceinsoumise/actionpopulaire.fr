import React, {
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";
import useSWR, { useSWRInfinite } from "swr";

import * as api from "@agir/groups/groupPage/api";

import {
  useDispatch,
  useSelector,
} from "@agir/front/globalContext/GlobalContext";

import {
  getMessages,
  getMessageById,
  getIsLoadingMessages,
  getIsUpdatingMessages,
} from "@agir/front/globalContext/reducers";

import * as messageActions from "@agir/front/globalContext/actions/messages";

const MESSAGES_PAGE_SIZE = 3;

export const useMessages = (group) => {
  const hasMessages = group && group.isMember && group.hasMessages;
  const dispatch = useDispatch();
  const messages = useSelector(getMessages);
  const isLoading = useSelector(getIsLoadingMessages);

  const getMessagesEndpoint = useCallback(
    (pageIndex) =>
      hasMessages
        ? api.getGroupPageEndpoint("getMessages", {
            groupPk: group.id,
            page: pageIndex + 1,
            pageSize: MESSAGES_PAGE_SIZE,
          })
        : null,
    [hasMessages, group]
  );

  const { data, size, setSize, mutate } = useSWRInfinite(getMessagesEndpoint);

  const messagesCount = useMemo(
    () =>
      !hasMessages || !Array.isArray(data) || !data[0] ? 0 : data[0].count,
    [hasMessages, data]
  );

  const loadMoreMessages = useMemo(
    () =>
      hasMessages && messagesCount > messages.length
        ? () => {
            setSize(size + 1);
          }
        : undefined,
    [hasMessages, messages.length, messagesCount, setSize, size]
  );

  useEffect(() => {
    !isLoading &&
      hasMessages &&
      !data &&
      dispatch(messageActions.loadMessages());
  }, [isLoading, dispatch, hasMessages, data]);

  useEffect(() => {
    data && dispatch(messageActions.setMessages(data));
  }, [dispatch, data]);

  useEffect(() => {
    mutate();
  }, [messages.length, mutate]);

  return {
    messages,
    loadMoreMessages,
    isLoadingMessages: isLoading,
  };
};

export const useMessage = (group, messagePk) => {
  const hasMessage = group && group.isMember && messagePk;
  const dispatch = useDispatch();
  const getMessage = useCallback((state) => getMessageById(state, messagePk), [
    messagePk,
  ]);
  const message = useSelector(getMessage);
  const isLoading = useSelector(getIsLoadingMessages);
  const isUpdating = useSelector(getIsUpdatingMessages);

  const getMessageEndpoint = useCallback(
    () =>
      hasMessage ? api.getGroupPageEndpoint("getMessage", { messagePk }) : null,
    [hasMessage, messagePk]
  );

  const { data } = useSWR(getMessageEndpoint);

  useEffect(() => {
    !isLoading &&
      hasMessage &&
      !data &&
      dispatch(messageActions.loadMessages());
  }, [isLoading, dispatch, hasMessage, data]);

  useEffect(() => {
    data && dispatch(messageActions.setMessage(data));
  }, [dispatch, data]);

  return {
    message,
    isLoading,
    isUpdating,
  };
};

export const useMessageActions = (props) => {
  const { user, group, isManager } = props;

  const dispatch = useDispatch();
  const isUpdating = useSelector(getIsUpdatingMessages);

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

  const confirmReportComment = useCallback((comment, message) => {
    setSelectedComment(comment);
    setSelectedMessage(message);
    setMessageAction("report");
  }, []);

  const confirmDeleteComment = useCallback((comment, message) => {
    setSelectedComment(comment);
    setSelectedMessage(message);
    setMessageAction("delete");
  }, []);

  const dismissMessageAction = useCallback(() => {
    setMessageAction("");
    setSelectedMessage(null);
    setSelectedComment(null);
    shouldDismiss.current = false;
  }, []);

  const writeNewComment = useCallback(
    (comment, message) => {
      dispatch(messageActions.createComment(comment, message));
    },
    [dispatch]
  );

  const saveMessage = useCallback(
    (message) => {
      if (message.id) {
        shouldDismiss.current = true;
        dispatch(messageActions.updateMessage(message));
      } else {
        shouldDismiss.current = true;
        dispatch(messageActions.createMessage(group, message));
      }
    },
    [dispatch, group]
  );

  const onDelete = useCallback(() => {
    if (!selectedMessage && !selectedComment) {
      return;
    }
    if (selectedMessage && selectedComment) {
      shouldDismiss.current = true;
      dispatch(messageActions.deleteComment(selectedComment, selectedMessage));
    } else if (selectedMessage) {
      shouldDismiss.current = true;
      dispatch(messageActions.deleteMessage(selectedMessage));
    }
  }, [dispatch, selectedMessage, selectedComment]);

  useEffect(() => {
    !isUpdating && shouldDismiss.current && dismissMessageAction();
  }, [isUpdating, dismissMessageAction]);

  const isAuthor = useMemo(() => {
    const isSelectedMessageAuthor =
      user && selectedMessage && selectedMessage.author.id === user.id;
    const isSelectedCommentAuthor =
      user && selectedComment && selectedComment.author.id === user.id;
    return isSelectedMessageAuthor || isSelectedCommentAuthor;
  }, [user, selectedMessage, selectedComment]);

  return {
    isUpdating,

    selectedMessage,
    selectedComment,

    messageAction,
    dismissMessageAction,

    writeNewMessage,
    editMessage,
    confirmDelete,
    confirmReport,
    saveMessage,

    writeNewComment,
    confirmDeleteComment,
    confirmReportComment,

    onDelete:
      messageAction === "delete" || (isManager && !isAuthor)
        ? onDelete
        : undefined,

    hasMessageModal: messageAction === "edit" || messageAction === "create",
    hasMessageActionModal:
      messageAction === "delete" || messageAction === "report",
  };
};

export const withMessageActions = (Component) => {
  const ConnectedComponent = (props) => {
    const messageActionProps = useMessageActions(props);
    return <Component {...messageActionProps} {...props} />;
  };
  return ConnectedComponent;
};
