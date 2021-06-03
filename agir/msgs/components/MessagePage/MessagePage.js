import PropTypes from "prop-types";
import React, { useCallback, useEffect } from "react";
import { useHistory } from "react-router-dom";
import styled from "styled-components";
import useSWR from "swr";

import style from "@agir/front/genericComponents/_variables.scss";

import { Hide } from "@agir/front/genericComponents/grid";
import Navigation from "@agir/front/dashboardComponents/Navigation";
import PageFadeIn from "@agir/front/genericComponents/PageFadeIn";
import Skeleton from "@agir/front/genericComponents/Skeleton";

import MessageThreadList from "./MessageThreadList";
import EmptyMessagePage from "./EmptyMessagePage";

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

const MessagePage = ({ messagePk }) => {
  const history = useHistory();
  const dispatch = useDispatch();

  const { data: session } = useSWR("/api/session");
  const { data: messages } = useSWR("/api/user/messages/");
  const { data: currentMessage } = useSWR(
    messagePk ? `/api/groupes/messages/${messagePk}/` : null
  );

  const handleSelect = useCallback(
    (messagePk) => {
      history.push(routeConfig.messages.getLink({ messagePk }));
    },
    [history]
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

  return (
    <>
      <PageFadeIn
        ready={typeof messages !== "undefined"}
        wait={
          <StyledPage>
            <Skeleton />
          </StyledPage>
        }
      >
        <StyledPage>
          {Array.isArray(messages) && messages.length > 0 ? (
            <MessageThreadList
              messages={messages}
              selectedMessage={currentMessage}
              onSelect={handleSelect}
              user={session?.user}
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
