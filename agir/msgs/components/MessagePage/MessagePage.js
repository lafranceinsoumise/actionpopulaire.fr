import PropTypes from "prop-types";
import React, { useCallback, useEffect, useRef, useState } from "react";
import { useHistory } from "react-router-dom";
import styled from "styled-components";
import useSWR, { mutate } from "swr";

import style from "@agir/front/genericComponents/_variables.scss";

import { Hide } from "@agir/front/genericComponents/grid";
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
  const { data: messages } = useSWR("/api/user/messages/");
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
    (messagePk) => {
      history.push(routeConfig.messages.getLink({ messagePk }));
    },
    [history]
  );

  return handleSelect;
};

const useMessageActions = (currentMessage, onSelectMessage) => {
  const shouldDismissAction = useRef(false);

  const [isLoading, setIsLoading] = useState(false);
  const [selectedGroupEvents, setSelectedGroupEvents] = useState([]);
  const [messageAction, setMessageAction] = useState("");

  const writeNewMessage = useCallback(() => {
    setMessageAction("create");
  }, []);

  const dismissMessageAction = useCallback(() => {
    setMessageAction("");
    shouldDismissAction.current = false;
  }, []);

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
      if (message.id) {
        // messageActions.updateMessage(message);
        return;
      }
      try {
        const result = await groupAPI.createMessage(message.group.id, message);
        if (result.data) {
          onSelectMessage(result.data.id);
          mutate("/api/user/messages/");
          setIsLoading(false);
        }
      } catch (e) {
        setIsLoading(false);
      }
    },
    [onSelectMessage]
  );

  useEffect(() => {
    !isLoading && shouldDismissAction.current && dismissMessageAction();
  }, [isLoading, dismissMessageAction]);

  return {
    isLoading,
    messageAction,
    selectedGroupEvents,

    writeNewMessage,
    dismissMessageAction,
    getSelectedGroupEvents,
    saveMessage,
  };
};

const MessagePage = ({ messagePk }) => {
  const { user, messages, messageRecipients, currentMessage } =
    useMessageSWR(messagePk);

  const onSelectMessage = useSelectMessage();

  const canWriteNewMessage =
    !!user && Array.isArray(messageRecipients) && messageRecipients.length > 0;

  const {
    isLoading,
    messageAction,
    selectedGroupEvents,
    writeNewMessage,
    dismissMessageAction,
    getSelectedGroupEvents,
    saveMessage,
  } = useMessageActions(currentMessage, onSelectMessage);

  return (
    <>
      <PageFadeIn
        ready={user && typeof messages !== "undefined"}
        wait={
          <StyledPage>
            <Skeleton />
          </StyledPage>
        }
      >
        <StyledPage>
          {canWriteNewMessage && (
            <MessageModal
              shouldShow={messageAction === "create"}
              onClose={dismissMessageAction}
              user={user}
              groups={messageRecipients}
              onSelectGroup={getSelectedGroupEvents}
              events={selectedGroupEvents}
              isLoading={isLoading}
              message={null}
              onSend={saveMessage}
            />
          )}
          {Array.isArray(messages) && messages.length > 0 ? (
            <MessageThreadList
              messages={messages}
              selectedMessagePk={messagePk}
              selectedMessage={currentMessage}
              onSelect={onSelectMessage}
              user={user}
              writeNewMessage={canWriteNewMessage ? writeNewMessage : undefined}
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
