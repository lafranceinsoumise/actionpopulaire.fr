import PropTypes from "prop-types";
import React, { useMemo } from "react";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";
import MessageCard from "@agir/front/genericComponents/MessageCard";
import PageFadeIn from "@agir/front/genericComponents/PageFadeIn";
import Skeleton from "@agir/front/genericComponents/Skeleton";

import GroupEventList from "@agir/groups/groupPage/GroupEventList";
import DiscussionAnnouncement from "@agir/groups/groupPage/DiscussionAnnouncement";

const RoutePreview = styled.div`
  margin: 0;
  padding: 0 0 1.5rem;
  width: 100%;

  @media (max-width: ${style.collapse}px) {
    margin-bottom: 0;
    padding: 1.5rem 1rem;
    background: ${style.black25};

    & + & {
      padding-top: 0;
    }
  }

  & > h3 {
    margin-top: 0;
    margin-bottom: 1rem;
    display: flex;
    flex-flow: row nowrap;
    align-items: center;
    font-size: 1rem;
    font-weight: 600;

    button {
      background: none;
      border: none;
      outline: none;
      display: flex;
      flex-flow: row nowrap;
      align-items: center;
      margin-left: 1rem;
      padding: 0;
      color: ${style.primary500};
      font-weight: inherit;
      font-size: inherit;

      @media (max-width: ${style.collapse}px) {
        margin-left: auto;
      }

      &:hover,
      &:focus {
        text-decoration: underline;
        cursor: pointer;
      }

      & > * {
        flex: 0 0 auto;
      }

      ${RawFeatherIcon} {
        margin-left: 0.5rem;
        margin-top: 1px;
      }
    }
  }

  & > article {
    margin-top: 1rem;
    border: 1px solid ${style.black200};
    padding: 1.5rem;
    width: 100%;

    @media (max-width: ${style.collapse}px) {
      border: none;
      box-shadow: ${style.elaborateShadow};
      padding: 1rem;
      background-color: ${style.white};
    }

    & > * {
      margin: 0;
      padding: 0;
    }
  }

  h3 + article {
    margin-top: 0;
  }
`;

export const AgendaRoutePreview = (props) => {
  const { upcomingEvents, pastEvents, goToAgendaTab } = props;

  const { lastEvent, isUpcoming } = useMemo(() => {
    if (Array.isArray(upcomingEvents) && upcomingEvents.length > 0) {
      return { isUpcoming: true, lastEvent: [upcomingEvents[0]] };
    }
    if (Array.isArray(pastEvents) && pastEvents.length > 0) {
      return { isUpcoming: false, lastEvent: [pastEvents[0]] };
    }
    return { isUpcoming: false, lastEvent: null };
  }, [upcomingEvents, pastEvents]);

  return (
    <PageFadeIn ready={!!lastEvent} wait={<Skeleton boxes={1} />}>
      <RoutePreview>
        <h3>
          <span>
            {isUpcoming ? "Événement à venir" : "Le dernier événement"}
          </span>
          {goToAgendaTab && (
            <button onClick={goToAgendaTab}>
              Voir tout{" "}
              <RawFeatherIcon
                name="arrow-right"
                width="1rem"
                height="1rem"
                strokeWidth={3}
              />
            </button>
          )}
        </h3>
        {lastEvent && <GroupEventList events={lastEvent} />}
      </RoutePreview>
    </PageFadeIn>
  );
};
AgendaRoutePreview.propTypes = {
  upcomingEvents: PropTypes.arrayOf(PropTypes.object),
  pastEvents: PropTypes.arrayOf(PropTypes.object),
  goToAgendaTab: PropTypes.func,
};

export const MessagesRoutePreview = (props) => {
  const { user, messages, goToMessagesTab, onClickMessage } = props;

  return (
    <PageFadeIn
      ready={Array.isArray(messages) && messages.length > 0}
      wait={<Skeleton boxes={1} />}
    >
      <RoutePreview>
        <h3>
          <span>Discussions</span>
          {goToMessagesTab && (
            <button onClick={goToMessagesTab}>
              Voir tout{" "}
              <RawFeatherIcon
                name="arrow-right"
                width="1rem"
                height="1rem"
                strokeWidth={3}
              />
            </button>
          )}
        </h3>
        <DiscussionAnnouncement isActive />
        <article>
          {messages && messages[0] && (
            <MessageCard
              user={user}
              message={messages[0]}
              comments={messages[0].recentComments}
              onClick={onClickMessage}
            />
          )}
        </article>
      </RoutePreview>
    </PageFadeIn>
  );
};
MessagesRoutePreview.propTypes = {
  user: PropTypes.object,
  messages: PropTypes.arrayOf(PropTypes.object),
  goToMessagesTab: PropTypes.func,
  onClickMessage: PropTypes.func,
};

export default RoutePreview;
