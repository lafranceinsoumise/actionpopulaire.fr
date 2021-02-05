import { useCallback, useMemo, useState } from "react";
import useSWR, { useSWRInfinite } from "swr";

import logger from "@agir/lib/utils/logger";

import * as api from "@agir/groups/groupPage/api";

const log = logger(__filename);

export const useMessages = (group) => {
  const [isLoading, setIsLoading] = useState(false);

  const hasMessages = group && group.isMember && group.hasMessages;
  const { data, error, size, setSize, mutate } = useSWRInfinite((pageIndex) =>
    hasMessages
      ? api.getGroupPageEndpoint("getMessages", {
          groupPk: group.id,
          page: pageIndex + 1,
          pageSize: 3,
        })
      : null
  );

  const messages = useMemo(() => {
    let messages = [];
    if (!hasMessages || error) {
      return messages;
    }
    if (!Array.isArray(data)) {
      return data;
    }
    data.forEach(({ results }) => {
      if (Array.isArray(results)) {
        messages = messages.concat(results);
      }
    });
    return messages;
  }, [hasMessages, data, error]);
  log.debug("Group messages", messages);

  const messagesCount = useMemo(() => {
    if (!hasMessages || !Array.isArray(data) || !data[0]) {
      return 0;
    }
    return data[0].count;
  }, [hasMessages, data]);

  const loadMoreMessages = useCallback(() => {
    setSize(size + 1);
  }, [setSize, size]);

  const createMessage = useCallback(
    async (message) => {
      try {
        setIsLoading(true);
        const response = await api.createMessage(group.id, message);
        setIsLoading(false);
        response.data && mutate();
      } catch (e) {
        setIsLoading(false);
      }
    },
    [group, mutate]
  );

  const updateMessage = useCallback(
    async (message) => {
      try {
        setIsLoading(true);
        const response = await api.updateMessage(message);
        response.data && mutate();
        setIsLoading(false);
      } catch (e) {
        setIsLoading(false);
      }
    },
    [mutate]
  );

  const deleteMessage = useCallback(
    async (message) => {
      try {
        setIsLoading(true);
        const response = await api.deleteMessage(message);
        !response.error && mutate();
        setIsLoading(false);
      } catch (e) {
        setIsLoading(false);
      }
    },
    [mutate]
  );

  const createComment = useCallback(
    async (comment, message) => {
      try {
        setIsLoading(true);
        const response = await api.createComment(message.id, comment);
        response.data && mutate();
        setIsLoading(false);
      } catch (e) {
        setIsLoading(false);
      }
    },
    [mutate]
  );

  const deleteComment = useCallback(
    async (comment) => {
      try {
        setIsLoading(true);
        const response = await api.deleteComment(comment);
        !response.error && mutate();
        setIsLoading(false);
      } catch (e) {
        setIsLoading(false);
      }
    },
    [mutate]
  );

  return {
    messages,
    loadMoreMessages:
      hasMessages && messages && messagesCount > messages.length
        ? loadMoreMessages
        : undefined,
    isLoadingMessages: hasMessages && (isLoading || !data),
    createMessage,
    updateMessage,
    deleteMessage,
    createComment,
    deleteComment,
  };
};

export const useMessage = (group, messagePk) => {
  const [isLoading, setIsLoading] = useState(false);

  const hasMessage = group && group.isMember && messagePk;
  const { data, error, mutate } = useSWR(
    hasMessage ? api.getGroupPageEndpoint("getMessage", { messagePk }) : null
  );
  log.debug("Group message #" + messagePk, data);

  const message = useMemo(() => (hasMessage && !error ? data : null), [
    hasMessage,
    error,
    data,
  ]);

  const updateMessage = useCallback(
    async (message) => {
      try {
        setIsLoading(true);
        const response = await api.updateMessage(message);
        response.data && mutate(() => response.data, false);
        setIsLoading(false);
      } catch (e) {
        setIsLoading(false);
      }
    },
    [mutate]
  );

  const deleteMessage = useCallback(
    async (message) => {
      try {
        setIsLoading(true);
        const response = await api.deleteMessage(message);
        !response.error && mutate(() => null, false);
        setIsLoading(false);
      } catch (e) {
        setIsLoading(false);
      }
    },
    [mutate]
  );

  const createComment = useCallback(
    async (comment, message) => {
      try {
        setIsLoading(true);
        const response = await api.createComment(message.id, comment);
        response.data &&
          mutate((data) => ({
            ...data,
            comments: [...(data.comments || []), response.data],
          }));
        setIsLoading(false);
      } catch (e) {
        setIsLoading(false);
      }
    },
    [mutate]
  );

  const deleteComment = useCallback(
    async (comment) => {
      try {
        setIsLoading(true);
        const response = await api.deleteComment(comment);
        !response.error &&
          mutate(
            (data) => ({
              ...data,
              comments: data.comments.filter((c) => c.id !== comment.id),
            }),
            false
          );
        setIsLoading(false);
      } catch (e) {
        setIsLoading(false);
      }
    },
    [mutate]
  );

  return {
    message,
    isLoading: isLoading || message === undefined,
    updateMessage,
    deleteMessage,
    createComment,
    deleteComment,
  };
};
