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

export const useMessageActions = (group) => {
  const isManager = (group && group.isManager) || false;

  const dispatch = useDispatch();
  const isUpdating = useSelector(getIsUpdatingMessages);

  const shouldDismiss = useRef(false);

  const [hasMessageModal, setHasMessageModal] = useState(false);

  const writeNewMessage = useCallback(() => {
    setHasMessageModal(true);
  }, []);

  const dismissMessageAction = useCallback(() => {
    setHasMessageModal(false);
    shouldDismiss.current = false;
  }, []);

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

  useEffect(() => {
    !isUpdating && shouldDismiss.current && dismissMessageAction();
  }, [isUpdating, dismissMessageAction]);

  return {
    isUpdating,
    hasMessageModal,
    dismissMessageAction,
    writeNewMessage: isManager ? writeNewMessage : undefined,
    saveMessage,
  };
};

export const withMessageActions = (Component) => {
  const ConnectedComponent = (props) => {
    const messageActionProps = useMessageActions(props);
    return <Component {...messageActionProps} {...props} />;
  };
  return ConnectedComponent;
};
