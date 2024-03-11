import React, {
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";
import useSWR from "swr";
import useSWRInfinite from "swr/infinite";

import * as api from "@agir/groups/utils/api";

import {
  useDispatch,
  useSelector,
} from "@agir/front/globalContext/GlobalContext";

import {
  getMessages,
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
  const isUpdating = useSelector(getIsUpdatingMessages);

  const wasUpdating = useRef(false);

  const getMessagesEndpoint = useCallback(
    (pageIndex) =>
      hasMessages
        ? api.getGroupEndpoint("getMessages", {
            groupPk: group.id,
            page: pageIndex + 1,
            pageSize: MESSAGES_PAGE_SIZE,
          })
        : null,
    [hasMessages, group],
  );

  const { data, size, setSize } = useSWRInfinite(getMessagesEndpoint, {
    revalidateAll: true,
  });

  const messagesCount = useMemo(
    () =>
      !hasMessages || !Array.isArray(data) || !data[0] ? 0 : data[0].count,
    [hasMessages, data],
  );

  const messagesData = useMemo(() => {
    let messages = [];
    if (Array.isArray(data)) {
      data.forEach(({ results }) => {
        if (Array.isArray(results)) {
          messages = messages.concat(results);
        }
      });
    }
    return messages;
  }, [data]);

  const loadMoreMessages = useMemo(() => {
    return messagesCount > size * MESSAGES_PAGE_SIZE
      ? () => {
          setSize(size + 1);
        }
      : undefined;
  }, [messagesCount, setSize, size]);

  useEffect(() => {
    // Mutate SWR data if messages length has changed through a local update
    wasUpdating.current &&
      setSize(Math.ceil(messages.length / MESSAGES_PAGE_SIZE));
  }, [setSize, messages.length]);

  useEffect(() => {
    wasUpdating.current = isUpdating;
  }, [isUpdating]);

  useEffect(() => {
    !isLoading &&
      hasMessages &&
      !data &&
      dispatch(messageActions.loadMessages());
  }, [isLoading, dispatch, hasMessages, data]);

  useEffect(() => {
    messagesData && dispatch(messageActions.setMessages(messagesData));
  }, [dispatch, messagesData]);

  useEffect(
    () => () => {
      dispatch(messageActions.clearMessages());
    },
    [dispatch],
  );

  return {
    messages,
    loadMoreMessages,
    isLoadingMessages: isLoading,
  };
};

export const useMessage = (group, messagePk) => {
  const hasMessage = messagePk && group && group.isMember;

  const getMessageEndpoint = useCallback(
    () => hasMessage && api.getGroupEndpoint("getMessage", { messagePk }),
    [hasMessage, messagePk],
  );

  const { data: message, error } = useSWR(getMessageEndpoint, {
    refreshInterval: 1000,
  });

  return {
    message: error ? null : message,
    isLoading:
      typeof group === "undefined" ||
      (hasMessage && typeof message === "undefined" && !error),
  };
};

export const useMessageActions = (props) => {
  const { user, group } = props;
  const isManager = (group && group.isManager) || false;

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
    [dispatch],
  );

  const saveMessage = useCallback(
    (message) => {
      shouldDismiss.current = true;
      dispatch(
        message.id
          ? messageActions.updateMessage(message)
          : messageActions.createMessage(group, message),
      );
    },
    [dispatch, group],
  );

  const onDelete = useCallback(() => {
    if (!selectedMessage && !selectedComment) {
      return;
    }
    if (selectedMessage && selectedComment) {
      dispatch(messageActions.deleteComment(selectedComment, selectedMessage));
    } else if (selectedMessage) {
      dispatch(messageActions.deleteMessage(selectedMessage));
    }
  }, [dispatch, selectedMessage, selectedComment]);

  const onReport = useCallback(() => {
    if (!selectedMessage && !selectedComment) {
      return;
    }
    if (selectedMessage && selectedComment) {
      dispatch(messageActions.reportComment(selectedComment));
    } else if (selectedMessage) {
      dispatch(messageActions.reportMessage(selectedMessage));
    }
  }, [dispatch, selectedMessage, selectedComment]);

  useEffect(() => {
    !isUpdating && shouldDismiss.current && dismissMessageAction();
  }, [isUpdating, dismissMessageAction]);

  const isAuthor = useMemo(() => {
    if (!selectedMessage && !selectedComment) {
      return false;
    }
    if (selectedComment) {
      return user && selectedComment && selectedComment.author.id === user.id;
    }
    return user && selectedMessage && selectedMessage.author.id === user.id;
  }, [user, selectedMessage, selectedComment]);

  return {
    isUpdating,

    selectedMessage,
    selectedComment,

    messageAction,
    dismissMessageAction,

    writeNewMessage: isManager ? writeNewMessage : undefined,
    editMessage: isManager ? editMessage : undefined,
    confirmDelete: isManager ? confirmDelete : undefined,
    confirmReport,
    saveMessage,

    writeNewComment,
    confirmDeleteComment,
    confirmReportComment,

    onDelete: messageAction === "delete" || isManager ? onDelete : undefined,

    onReport:
      messageAction === "report" || (isManager && !isAuthor)
        ? onReport
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
