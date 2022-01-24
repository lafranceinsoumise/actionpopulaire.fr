import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useHistory, useLocation } from "react-router-dom";
import { useTimeout } from "react-use";
import useSWR, { mutate } from "swr";
import useSWRInfinite from "swr/infinite";
import { validate as uuidValidate } from "uuid";

import axios from "@agir/lib/utils/axios";
import * as groupAPI from "@agir/groups/api";
import { routeConfig } from "@agir/front/app/routes.config";
import { setBackLink } from "@agir/front/globalContext/actions";
import { useDispatch } from "@agir/front/globalContext/GlobalContext";

export const useUnreadMessageCount = () => {
  const [isReady] = useTimeout(3000);
  const { data: session } = useSWR("/api/session/");
  const ready = isReady() && session?.user;
  const { data } = useSWR(ready && "/api/user/messages/unread_count/", {
    refreshInterval: 10000,
    dedupingInterval: 10000,
    focusThrottleInterval: 10000,
    shouldRetryOnError: false,
    revalidateIfStale: false,
  });

  return data?.unreadMessageCount && !isNaN(parseInt(data.unreadMessageCount))
    ? parseInt(data.unreadMessageCount)
    : 0;
};

const MESSAGES_LIST_SIZE = 10;

export const useMessageSWR = (messagePk, selectMessage) => {
  const dispatch = useDispatch();
  const isAutoRefreshPausedRef = useRef(false);
  const { data: session } = useSWR("/api/session/");

  const {
    data,
    error: errorMessages,
    isValidating: isValidatingMessages,
    mutate: mutateMessages,
    size,
    setSize,
  } = useSWRInfinite(
    (index) =>
      `/api/user/messages/?page=${index + 1}&page_size=${MESSAGES_LIST_SIZE}`
  );

  const messages = useMemo(() => {
    const messages = {};
    const messageIds = [];
    if (Array.isArray(data)) {
      data.forEach(({ results }) => {
        if (Array.isArray(results)) {
          results.forEach((message) => {
            if (!messages[message.id]) {
              messages[message.id] = message;
              messageIds.push(message.id);
            }
          });
        }
      });
    }
    return messageIds.map((id) => messages[id]);
  }, [data]);

  const isLoadingInitialData = !data && !errorMessages;
  const isLoadingMore =
    isLoadingInitialData ||
    (size > 0 && data && typeof data[size - 1] === "undefined");

  const messageCount = (data && data[data.length - 1]?.count) || 0;
  const isEmpty = messageCount === 0;
  const isReachingEnd =
    isEmpty ||
    messages.length === messageCount ||
    (data && data[data.length - 1]?.results?.length < MESSAGES_LIST_SIZE);
  const isRefreshing = isValidatingMessages && data && data.length === size;

  const loadMore = useCallback(() => {
    console.log("INFINITE SCROLL ! ");
    setSize(size + 1);
  }, [setSize, size]);

  const { data: messageRecipients } = useSWR("/api/user/messages/recipients/");
  const {
    data: currentMessage,
    error,
    isValidating,
    mutate: mutateMessage,
  } = useSWR(
    messagePk && uuidValidate(messagePk)
      ? `/api/groupes/messages/${messagePk}/`
      : null
  );
  const { pathname } = useLocation();

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
  }, [dispatch, currentMessageId, pathname]);

  useEffect(() => {
    !isValidating &&
      error?.response?.status === 404 &&
      selectMessage &&
      selectMessage(null, true);
  }, [error, isValidating, selectMessage]);

  useEffect(() => {
    if (isValidating || !messages || !currentMessage) {
      return;
    }
    const updatedMessage = messages.find((m) => m.id === currentMessage.id);
    if (
      updatedMessage &&
      updatedMessage.lastUpdate === currentMessage.lastUpdate
    ) {
      return;
    }
    mutateMessage();
  }, [isValidating, messages, currentMessage, mutateMessage]);

  return {
    user: session?.user,
    messages,
    //
    errorMessages,
    isLoadingInitialData,
    isLoadingMore,
    isRefreshing,
    loadMore: isEmpty || isReachingEnd ? undefined : loadMore,
    mutateMessages,
    //
    messageRecipients,
    currentMessage,
    isAutoRefreshPausedRef,
  };
};

export const useSelectMessage = () => {
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

export const useMessageActions = (
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
    if (!user) {
      return false;
    }
    if (!selectedMessage && !selectedComment) {
      return false;
    }
    if (selectedComment) {
      return selectedComment && selectedComment.author?.id === user.id;
    }
    return selectedMessage && selectedMessage.author?.id === user.id;
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
          mutate(
            `/api/groupes/messages/${message.id}/`,
            () => result.data,
            false
          );
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
        mutate(
          `/api/groupes/messages/${selectedMessage.id}/`,
          (message) => ({
            ...message,
            comments: Array.isArray(message.comments)
              ? [...message.comments, response.data]
              : [response.data],
          }),
          false
        );
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
      mutate(`/api/groupes/messages/${selectedMessage.id}/`, (data) => ({
        ...data,
        comments: data.comments.filter(
          (comment) => comment.id === selectedComment.id
        ),
      }));
    } else if (messageAction === "delete") {
      mutate(
        `/api/user/messages/`,
        (data) => data.filter((message) => message.id !== selectedMessage.id),
        false
      );
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
