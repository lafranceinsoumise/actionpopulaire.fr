import PropTypes from "prop-types";
import React, { useMemo, Fragment } from "react";
import styled from "styled-components";

import * as style from "@agir/front/genericComponents/_variables.scss";

import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";
import { MessageReadonlyCard } from "@agir/front/genericComponents/MessageCard";
import PageFadeIn from "@agir/front/genericComponents/PageFadeIn";
import Skeleton from "@agir/front/genericComponents/Skeleton";
import Spacer from "@agir/front/genericComponents/Spacer";

import GroupEventList from "@agir/groups/groupPage/GroupEventList";

const RoutePreview = styled.div`
  margin: 0;
  padding: 0 0 1.5rem;
  width: 100%;

  @media (max-width: ${style.collapse}px) {
    margin-bottom: 0;
    padding: 1.5rem 1rem;
    background: ${style.black25};

    & + & {
      border-top: 1px solid ${style.black100};
    }
  }

  & > div {
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
      padding: 0;
      width: 100%;

      @media (max-width: ${style.collapse}px) {
        border: none;
      }

      & > * {
        @media (max-width: ${style.collapse}px) {
          margin: 0;
          background-color: ${style.white};

          & + & {
            margin-top: 1rem;
          }
        }
      }
    }

    & > h3 + article {
      margin-top: 0;
    }
  }
`;

export const AgendaRoutePreview = (props) => {
  const { group, upcomingEvents, pastEvents, goToAgendaTab } = props;

  const nextEvents = useMemo(() => {
    if (Array.isArray(upcomingEvents) && upcomingEvents.length > 0) {
      return upcomingEvents.slice(0, 3);
    }
    return [];
  }, [upcomingEvents]);

  const lastEvents = useMemo(() => {
    if (
      Array.isArray(pastEvents) &&
      pastEvents.length > 0 &&
      nextEvents.length < 3
    ) {
      return pastEvents.slice(0, 3 - nextEvents.length);
    }
    return [];
  }, [nextEvents.length, pastEvents]);

  return (
    <>
      {group.hasUpcomingEvents && (
        <RoutePreview>
          <PageFadeIn
            ready={nextEvents.length + lastEvents.length > 0}
            wait={<Skeleton boxes={1} />}
          >
            {nextEvents.length > 0 && (
              <>
                <h3>
                  <span>À venir</span>
                  {goToAgendaTab && (
                    <button onClick={goToAgendaTab}>
                      Agenda{" "}
                      <RawFeatherIcon
                        name="arrow-right"
                        width="1rem"
                        height="1rem"
                        strokeWidth={3}
                      />
                    </button>
                  )}
                </h3>
                <GroupEventList events={nextEvents} />
              </>
            )}
          </PageFadeIn>
        </RoutePreview>
      )}
      {group.hasPastEvents && (
        <RoutePreview>
          <PageFadeIn
            ready={nextEvents.length + lastEvents.length > 0}
            wait={<Skeleton boxes={1} />}
          >
            {lastEvents.length > 0 && (
              <>
                <h3>
                  <span>
                    Dernier{lastEvents.length > 1 ? "s" : ""} événement
                    {lastEvents.length > 1 ? "s" : ""}
                  </span>
                  {goToAgendaTab && (
                    <button onClick={goToAgendaTab}>
                      Agenda{" "}
                      <RawFeatherIcon
                        name="arrow-right"
                        width="1rem"
                        height="1rem"
                        strokeWidth={3}
                      />
                    </button>
                  )}
                </h3>
                <GroupEventList events={lastEvents} />
              </>
            )}
          </PageFadeIn>
        </RoutePreview>
      )}
    </>
  );
};

AgendaRoutePreview.propTypes = {
  group: PropTypes.object,
  upcomingEvents: PropTypes.arrayOf(PropTypes.object),
  pastEvents: PropTypes.arrayOf(PropTypes.object),
  goToAgendaTab: PropTypes.func,
};

export const MessagesRoutePreview = (props) => {
  const { group, user, messages, goToMessagesTab, isLoadingMessages } = props;

  if (
    (!isLoadingMessages && !Array.isArray(messages)) ||
    messages.length === 0
  ) {
    return null;
  }
  return (
    <RoutePreview>
      <PageFadeIn ready={!isLoadingMessages} wait={<Skeleton boxes={1} />}>
        <h3>
          <span>Derniers messages</span>
          {goToMessagesTab && (
            <button onClick={goToMessagesTab}>
              Messages{" "}
              <RawFeatherIcon
                name="arrow-right"
                width="1rem"
                height="1rem"
                strokeWidth={3}
              />
            </button>
          )}
        </h3>
        <article>
          {Array.isArray(messages) &&
            messages.map((message) => (
              <Fragment key={message.id}>
                <MessageReadonlyCard
                  user={user}
                  message={message}
                  comments={message.comments || message.recentComments || []}
                  backLink={{
                    route: "groupDetails",
                    routeParams: { groupPk: group.id, activeTab: "messages" },
                  }}
                />
                <Spacer size="1.5rem" style={{ backgroundColor: "inherit" }} />
              </Fragment>
            ))}
        </article>
      </PageFadeIn>
    </RoutePreview>
  );
};
MessagesRoutePreview.propTypes = {
  group: PropTypes.object,
  user: PropTypes.object,
  messages: PropTypes.arrayOf(PropTypes.object),
  goToMessagesTab: PropTypes.func,
  onClickMessage: PropTypes.func,
  isLoadingMessages: PropTypes.bool,
};

export default RoutePreview;
