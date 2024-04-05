import PropTypes from "prop-types";
import React, { Fragment } from "react";
import styled from "styled-components";

import * as style from "@agir/front/genericComponents/_variables.scss";

import { useMessageActions } from "@agir/groups/groupPage/hooks/messages";

import Button from "@agir/front/genericComponents/Button";
import Spacer from "@agir/front/genericComponents/Spacer";
import { MessageReadonlyCard } from "@agir/front/genericComponents/MessageCard";
import PageFadeIn from "@agir/front/genericComponents/PageFadeIn";
import Skeleton from "@agir/front/genericComponents/Skeleton";
import { ResponsiveLayout } from "@agir/front/genericComponents/grid";

import MessageModalTrigger, {
  FloatingTrigger as FloatingMessageModalTrigger,
} from "@agir/front/formComponents/MessageModal/Trigger";
import MessageModal from "@agir/front/formComponents/MessageModal/Modal";
import { PromoMessage } from "@agir/groups/messages/PromoMessageModal";

const StyledButton = styled.div`
  text-align: center;

  ${Button} {
    &,
    &:hover,
    &:focus,
    &:active {
      background-color: white;
      width: auto;
      margin: 0 auto;
      justify-content: center;

      @media (max-width: ${style.collapse}px) {
        width: 100%;
        margin-bottom: 1.5rem;
        font-size: 0.875rem;
        box-shadow: ${style.elaborateShadow};
      }
    }
  }
`;
const StyledMessages = styled.div`
  margin-top: 1rem;
  display: flex;
  justify-content: center;
  align-items: center;
  flex-direction: column;

  @media (max-width: ${style.collapse}px) {
    background-color: ${style.black50};
  }
`;
const StyledWrapper = styled.div`
  @media (max-width: ${style.collapse}px) {
    margin-top: 1rem;
  }

  & > h3 {
    margin: 0;
    padding: 0 0 1.5rem 0;

    @media (max-width: ${style.collapse}px) {
      padding: 1.5rem 1rem 0.5rem;
    }
  }
`;

export const GroupMessages = (props) => {
  const {
    group,
    user,
    events,
    messages,
    isLoading,
    loadMoreEvents,
    loadMoreMessages,
  } = props;

  const {
    isUpdating,
    hasMessageModal,
    dismissMessageAction,
    writeNewMessage,
    saveMessage,
  } = useMessageActions(group);

  const isManager = group && group.isManager;

  return (
    <StyledWrapper>
      <h3>
        <PageFadeIn
          ready={!isLoading && Array.isArray(messages)}
          wait={
            <Skeleton
              boxes={1}
              style={{ width: "50%", height: "2em", margin: 0 }}
            />
          }
        >
          Messages
        </PageFadeIn>
      </h3>
      {Array.isArray(messages) && writeNewMessage ? (
        <ResponsiveLayout
          MobileLayout={FloatingMessageModalTrigger}
          DesktopLayout={MessageModalTrigger}
          onClick={writeNewMessage}
          outlined
        />
      ) : null}
      {saveMessage ? (
        <MessageModal
          shouldShow={hasMessageModal}
          onClose={dismissMessageAction}
          user={user}
          events={events}
          loadMoreEvents={loadMoreEvents}
          isLoading={isUpdating}
          onSend={saveMessage}
        />
      ) : null}
      <PageFadeIn
        ready={!isLoading && Array.isArray(messages)}
        wait={<Skeleton style={{ margin: "1rem 0" }} />}
      >
        <StyledMessages>
          {Array.isArray(messages) && messages.length > 0
            ? messages.map((message) => (
                <Fragment key={message.id}>
                  <MessageReadonlyCard
                    user={user}
                    message={message}
                    comments={message.comments || message.recentComments}
                    backLink={{
                      route: "groupDetails",
                      routeParams: { groupPk: group.id, activeTab: "messages" },
                    }}
                  />
                  <Spacer size="1.5rem" />
                </Fragment>
              ))
            : null}

          {isManager && !isLoading && !messages?.length && (
            <PromoMessage onClick={writeNewMessage} />
          )}

          {typeof loadMoreMessages === "function" ? (
            <StyledButton>
              <Button
                color="white"
                onClick={loadMoreMessages}
                disabled={isLoading}
                icon="chevron-down"
                rightIcon
              >
                Charger plus de messages
              </Button>
            </StyledButton>
          ) : null}
        </StyledMessages>
      </PageFadeIn>
    </StyledWrapper>
  );
};
GroupMessages.propTypes = {
  group: PropTypes.shape({
    id: PropTypes.string,
    isManager: PropTypes.bool,
  }),
  user: PropTypes.object,
  events: PropTypes.arrayOf(PropTypes.object),
  messages: PropTypes.arrayOf(PropTypes.object),
  isLoading: PropTypes.bool,
  isManager: PropTypes.bool,
  onClick: PropTypes.func,
  loadMoreEvents: PropTypes.func,
  loadMoreMessages: PropTypes.func,
};

export default GroupMessages;
