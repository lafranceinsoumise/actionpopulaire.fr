import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useHistory } from "react-router-dom";
import { useTimeout } from "react-use";
import useSWR, { mutate } from "swr";
import useSWRImmutable from "swr/immutable";
import useSWRInfinite from "swr/infinite";
import { validate as uuidValidate } from "uuid";

import axios from "@agir/lib/utils/axios";
import * as groupAPI from "@agir/groups/utils/api";
import { routeConfig } from "@agir/front/app/routes.config";
import { setBackLink } from "@agir/front/globalContext/actions";
import { useDispatch } from "@agir/front/globalContext/GlobalContext";
import { useCurrentLocation } from "@agir/front/app/utils";

const MESSAGES_PAGE_SIZE = 10;
const COMMENTS_PAGE_SIZE = 15;

export const useUnreadMessageCount = () => {
  const [isReady] = useTimeout(3000);
  const { data: session } = useSWRImmutable("/api/session/");
  const { data } = useSWR(
    isReady() && session?.user && "/api/user/messages/unread_count/",
    {
      refreshInterval: 10000,
      dedupingInterval: 10000,
      focusThrottleInterval: 10000,
      shouldRetryOnError: false,
      revalidateIfStale: false,
    },
  );

  return data?.unreadMessageCount && !isNaN(parseInt(data.unreadMessageCount))
    ? parseInt(data.unreadMessageCount)
    : 0;
};

export const useCommentsSWR = (messagePk) => {
  const { data, error, isValidating, mutate, size, setSize } = useSWRInfinite(
    (index) =>
      messagePk &&
      `/api/groupes/messages/${messagePk}/comments/?page=${
        index + 1
      }&page_size=${COMMENTS_PAGE_SIZE}`,
    {
      revalidateIfStale: false,
      revalidateOnFocus: false,
      revalidateOnReconnect: false,
    },
  );

  const comments = useMemo(() => {
    const comments = {};
    const commentsIds = [];
    if (Array.isArray(data)) {
      data.forEach(({ results }) => {
        if (Array.isArray(results)) {
          results.forEach((comment) => {
            if (!comments[comment.id]) {
              comments[comment.id] = comment;
              commentsIds.push(comment.id);
            }
          });
        }
      });
    }
    return commentsIds.reverse().map((id) => comments[id]);
  }, [data]);

  const isLoadingInitialData = !data && !error;
  const isLoadingMore =
    isLoadingInitialData ||
    (size > 0 && data && typeof data[size - 1] === "undefined");

  const commentsCount = (data && data[data.length - 1]?.count) || 0;
  const isEmpty = commentsCount === 0;
  const isReachingEnd =
    isEmpty ||
    comments.length === commentsCount ||
    (data && data[data.length - 1]?.results?.length < COMMENTS_PAGE_SIZE);
  const isRefreshing = isValidating && data && data.length === size;

  const loadMore = useCallback(() => setSize(size + 1), [setSize, size]);
  const isAutoRefreshPausedRef = useRef(false);

  return {
    comments,
    commentsCount,
    error,
    isLoadingInitialData,
    isLoadingMore,
    isRefreshing,
    loadMore: isEmpty || isReachingEnd ? undefined : loadMore,
    mutate,
    isAutoRefreshPausedRef,
  };
};

export const useMessageSWR = (messagePk) => {
  const dispatch = useDispatch();
  const pathname = useCurrentLocation();

  const isAutoRefreshPausedRef = useRef(false);

  const { data: session } = useSWRImmutable("/api/session/");
  const user = session?.user;

  const {
    data,
    error: errorMessages,
    isValidating: isValidatingMessages,
    mutate: mutateMessages,
    size,
    setSize,
  } = useSWRInfinite(
    (index) =>
      user &&
      `/api/user/messages/?page=${index + 1}&page_size=${MESSAGES_PAGE_SIZE}`,
    {
      revalidateIfStale: false,
      revalidateOnFocus: false,
      revalidateOnReconnect: false,
    },
  );
  const { data: messageRecipients } = useSWRImmutable(
    data && "/api/user/messages/recipients/",
  );
  const {
    data: currentMessage,
    error,
    isValidating,
    mutate: mutateMessage,
  } = useSWRImmutable(
    data && messagePk && uuidValidate(messagePk)
      ? `/api/groupes/messages/${messagePk}/`
      : null,
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
    (data && data[data.length - 1]?.results?.length < MESSAGES_PAGE_SIZE);
  const isRefreshing = isValidatingMessages && data && data.length === size;

  const loadMore = useCallback(() => setSize(size + 1), [setSize, size]);

  const currentMessageId = currentMessage?.id;

  const onSelectMessage = useSelectMessage();

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
            },
      ),
    );
  }, [dispatch, currentMessageId, pathname]);

  useEffect(() => {
    !isValidating &&
      error?.response?.status === 404 &&
      onSelectMessage(null, true);
  }, [error, isValidating, onSelectMessage]);

  useEffect(() => {
    if (isValidating || !Array.isArray(messages) || !currentMessage) {
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
    user,
    messages,
    messageCount,
    errorMessages,
    isLoadingInitialData,
    isLoadingMore,
    isRefreshing,
    loadMore: isEmpty || isReachingEnd ? undefined : loadMore,
    mutateMessages,
    messageRecipients,
    currentMessage,
    isAutoRefreshPausedRef,
    onSelectMessage,
  };
};

export const useSelectMessage = () => {
  const history = useHistory();
  const handleSelect = useCallback(
    (messagePk, doNotPush = false) => {
      const fn = doNotPush ? history.replace : history.push;
      fn(routeConfig.messages.getLink({ messagePk }), {
        backLink: { route: "messages" },
      });
    },
    [history],
  );

  return handleSelect;
};

export const useMessageActions = (
  user,
  messageRecipients,
  selectedMessage,
  onSelectMessage,
  mutateMessages,
  mutateComments,
) => {
  const shouldDismissAction = useRef(false);

  const [isLoading, setIsLoading] = useState(false);
  const [selectedGroupEvents, setSelectedGroupEvents] = useState([]);
  const [selectedComment, setSelectedComment] = useState(null);
  const [messageAction, setMessageAction] = useState("");
  const [messageErrors, setMessageErrors] = useState(null);
  const [commentErrors, setCommentErrors] = useState(null);

  const canWriteNewMessage =
    !!user && Array.isArray(messageRecipients) && messageRecipients.length > 0;

  const canEditSelectedMessage = useMemo(
    () =>
      canWriteNewMessage &&
      selectedMessage?.group &&
      messageRecipients.some((r) => r.id === selectedMessage.group.id),
    [canWriteNewMessage, messageRecipients, selectedMessage],
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
        `/api/groupes/${group.id}/evenements/`,
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
      setMessageErrors(null);
      shouldDismissAction.current = false;
      try {
        const { data, error } = message.id
          ? await groupAPI.updateMessage(message)
          : await groupAPI.createMessage(message.group.id, message);

        if (error) {
          typeof error === "string"
            ? setMessageErrors({ details: "Une erreur est survenue" })
            : setMessageErrors(error);
          setIsLoading(false);
          return;
        }
        shouldDismissAction.current = true;
        setIsLoading(false);
        mutateMessages();
        if (message.id) {
          mutate(`/api/groupes/messages/${message.id}/`, () => data, false);
        } else {
          onSelectMessage(data.id);
        }
      } catch (e) {
        setIsLoading(false);
        setMessageErrors({ details: e.message });
      }
    },
    [onSelectMessage, mutateMessages],
  );

  const writeNewComment = useCallback(
    async (comment) => {
      setIsLoading(true);
      setCommentErrors(null);
      try {
        const { error } = await groupAPI.createComment(
          selectedMessage.id,
          comment,
        );
        if (error) {
          typeof error === "string"
            ? setCommentErrors({ details: "Une erreur est survenue" })
            : setCommentErrors(error);
          setIsLoading(false);
          return;
        }
        setIsLoading(false);
        mutateComments();
        onSelectMessage(selectedMessage.id);
      } catch (e) {
        setIsLoading(false);
        setCommentErrors({ details: e.message });
      }
    },
    [selectedMessage, onSelectMessage, mutateComments],
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
      mutateComments();
    } else if (messageAction === "delete") {
      onSelectMessage(null);
      mutateMessages();
    }
    setMessageAction("");
    setSelectedComment(null);
    shouldDismissAction.current = false;
  }, [
    messageAction,
    selectedComment,
    selectedMessage,
    onSelectMessage,
    mutateMessages,
    mutateComments,
  ]);

  useEffect(() => {
    !isLoading && shouldDismissAction.current && dismissMessageAction();
  }, [isLoading, dismissMessageAction]);

  return {
    isLoading,

    messageAction,
    selectedGroupEvents,
    selectedComment,

    messageErrors,
    commentErrors,

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
