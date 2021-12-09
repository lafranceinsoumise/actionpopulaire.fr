import PropTypes from "prop-types";
import React, { useEffect, useRef } from "react";
import { useIntersection, usePrevious } from "react-use";
import styled from "styled-components";
import useSWR from "swr";
import { useToast } from "@agir/front/globalContext/hooks";

import style from "@agir/front/genericComponents/_variables.scss";

import { routeConfig } from "@agir/front/app/routes.config";

import MessageCard from "@agir/front/genericComponents/MessageCard";
import PageFadeIn from "@agir/front/genericComponents/PageFadeIn";
import Panel from "@agir/front/genericComponents/Panel";
import { ResponsiveLayout } from "@agir/front/genericComponents/grid";

import MessageThreadMenu from "./MessageThreadMenu";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";
import { switchMessageMuted, getGroupEndpoint } from "@agir/groups/api.js";

const StyledContent = styled.article`
  height: 100%;
  overflow-x: hidden;
  overflow-y: auto;

  @media (max-width: ${style.collapse}px) {
    padding-bottom: 0;
  }

  & > * {
    box-shadow: none;
    border: none;
    min-height: 100%;

    & > * {
      border: none;
    }
  }
`;
const StyledList = styled.main`
  width: 100%;
  height: 100%;
  display: flex;
  align-items: stretch;
  flex-flow: row nowrap;
  box-shadow: 0px 0px 3px rgba(0, 0, 0, 0.15), 0px 3px 3px rgba(0, 35, 44, 0.1);
  border-radius: 4px;
  border: 1px solid ${style.black200};
  overflow: hidden;

  @media (max-width: ${style.collapse}px) {
    display: block;
    border: none;
    border-radius: none;
    box-shadow: none;
  }

  & > * {
    flex: 1 1 auto;
    height: 100%;
    overflow-x: hidden;
    overflow-y: auto;

    &:first-child {
      @media (min-width: ${style.collapse}px) {
        flex: 0 0 400px;
      }
    }
  }
`;

const BlockMuteMessage = styled.div`
  height: 56px;
  display: flex;
  flex-direction: column;
  align-items: end;
  justify-content: center;
  padding-right: 10px;
  ${({ isActive }) => !isActive && `color: red;`}

  ${RawFeatherIcon}:hover {
    cursor: pointer;
    color: ${style.primary500};
  }
`;

const useAutoScrollToBottom = (commentLength = 0, messageId) => {
  const scrollableRef = useRef(null);
  const bottomRef = useRef(null);
  const hasNewComments = useRef(false);

  const intersection = useIntersection(bottomRef, {
    root: scrollableRef.current,
    rootMargin: "0px",
    threshold: 1,
  });

  const isScrolledBottom = !!intersection?.isIntersecting;
  const wasScrolledBottom = usePrevious(isScrolledBottom);

  useEffect(() => {
    hasNewComments.current = true;
  }, [commentLength]);

  useEffect(() => {
    hasNewComments.current = false;
  }, [messageId]);

  useEffect(() => {
    if (
      bottomRef.current &&
      wasScrolledBottom &&
      !isScrolledBottom &&
      hasNewComments.current
    ) {
      bottomRef.current.scrollIntoView(false);
    }
    hasNewComments.current = false;
  }, [isScrolledBottom, wasScrolledBottom]);

  return [scrollableRef, bottomRef];
};

const ON = "on";

const DesktopThreadList = (props) => {
  const {
    isLoading,
    user,
    messages,
    selectedMessagePk,
    selectedMessage,
    onSelect,
    onEdit,
    onComment,
    onReport,
    onDelete,
    onReportComment,
    onDeleteComment,
    writeNewMessage,
    notificationSettingLink,
  } = props;

  const [scrollableRef, bottomRef] = useAutoScrollToBottom(
    selectedMessage?.comments?.length,
    selectedMessagePk
  );

  const sendToast = useToast();

  const { data, mutate } = useSWR(
    getGroupEndpoint("getMessageMuted", { messagePk: selectedMessage?.id })
  );
  const isActive = data && data.data === ON;

  const switchNotificationMessage = async () => {
    const { data } = await switchMessageMuted(selectedMessage);
    mutate(() => data);
    let text =
      "Vous ne recevrez plus de notifications reliées à ce fil de messages";
    let type = "INFO";
    if (data.data === ON) {
      text = "Les notifications reliées à ce fil de message sont réactivées";
      type = "SUCCESS";
    }
    sendToast(text, type, { autoClose: true });
  };

  useEffect(() => {
    // Autoselect first message on desktop
    !selectedMessagePk &&
      Array.isArray(messages) &&
      messages[0] &&
      onSelect(messages[0].id, true);
  }, [messages, selectedMessagePk, onSelect]);

  return (
    <StyledList>
      <MessageThreadMenu
        isLoading={isLoading}
        messages={messages}
        selectedMessageId={selectedMessage?.id}
        notificationSettingLink={notificationSettingLink}
        onSelect={onSelect}
        writeNewMessage={writeNewMessage}
      />
      <div style={{ display: "flex", flexDirection: "column" }}>
        {!!selectedMessage && (
          <BlockMuteMessage isActive={isActive}>
            <RawFeatherIcon
              name={`bell${!isActive ? "-off" : ""}`}
              onClick={switchNotificationMessage}
            />
          </BlockMuteMessage>
        )}
        <StyledContent ref={scrollableRef}>
          <PageFadeIn ready={selectedMessagePk && selectedMessage}>
            {!!selectedMessage && (
              <MessageCard
                autoScrollOnComment
                isLoading={isLoading}
                user={user}
                message={selectedMessage}
                comments={selectedMessage.comments}
                onEdit={onEdit}
                onComment={onComment}
                onReport={onReport}
                onDelete={onDelete}
                onReportComment={onReportComment}
                onDeleteComment={onDeleteComment}
                isManager={selectedMessage.group.isManager}
                groupURL={routeConfig.groupDetails.getLink({
                  groupPk: selectedMessage.group.id,
                })}
              />
            )}
            <span
              style={{ width: 1, height: 0 }}
              aria-hidden={true}
              ref={bottomRef}
            />
          </PageFadeIn>
        </StyledContent>
      </div>
    </StyledList>
  );
};

const MobileThreadList = (props) => {
  const {
    isLoading,
    user,
    messages,
    selectedMessage,
    selectedMessagePk,
    onSelect,
    onEdit,
    onComment,
    onReport,
    onDelete,
    onReportComment,
    onDeleteComment,
    writeNewMessage,
    notificationSettingLink,
  } = props;

  const [scrollableRef, bottomRef] = useAutoScrollToBottom(
    selectedMessage?.comments?.length,
    selectedMessagePk
  );

  return (
    <StyledList>
      <MessageThreadMenu
        isLoading={isLoading}
        messages={messages}
        selectedMessageId={selectedMessage?.id}
        notificationSettingLink={notificationSettingLink}
        onSelect={onSelect}
        writeNewMessage={writeNewMessage}
      />
      <Panel
        style={{
          paddingLeft: "0",
          paddingRight: "0",
          paddingBottom: "0",
          background: "white",
        }}
        shouldShow={!!selectedMessage}
        noScroll
        isBehindTopBar
      >
        <StyledContent ref={scrollableRef}>
          {selectedMessage && (
            <MessageCard
              autoScrollOnComment
              withMobileCommentField
              isLoading={isLoading}
              user={user}
              message={selectedMessage}
              comments={selectedMessage?.comments}
              onEdit={onEdit}
              onComment={selectedMessage && onComment ? onComment : undefined}
              onReport={onReport}
              onDelete={onDelete}
              onReportComment={onReportComment}
              onDeleteComment={onDeleteComment}
              isManager={selectedMessage?.group.isManager}
              groupURL={routeConfig.groupDetails.getLink({
                groupPk: selectedMessage?.group.id,
              })}
            />
          )}
          <span
            style={{ width: 1, height: 0 }}
            aria-hidden={true}
            ref={bottomRef}
          />
        </StyledContent>
      </Panel>
    </StyledList>
  );
};

const MessageThreadList = (props) => {
  return (
    <ResponsiveLayout
      MobileLayout={MobileThreadList}
      DesktopLayout={DesktopThreadList}
      {...props}
    />
  );
};

DesktopThreadList.propTypes =
  MobileThreadList.propTypes =
  MessageThreadList.propTypes =
    {
      isLoading: PropTypes.bool,
      messages: PropTypes.arrayOf(PropTypes.object),
      selectedMessagePk: PropTypes.string,
      selectedMessage: PropTypes.object,
      user: PropTypes.shape({
        id: PropTypes.string.isRequired,
        image: PropTypes.string,
        displayName: PropTypes.string,
      }),
      notificationSettingLink: PropTypes.string,
      onSelect: PropTypes.func,
      onEdit: PropTypes.func,
      onComment: PropTypes.func,
      onReport: PropTypes.func,
      onDelete: PropTypes.func,
      onReportComment: PropTypes.func,
      onDeleteComment: PropTypes.func,
      writeNewMessage: PropTypes.func,
    };

export default MessageThreadList;
