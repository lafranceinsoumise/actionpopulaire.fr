import PropTypes from "prop-types";
import React, { useEffect } from "react";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

import { routeConfig } from "@agir/front/app/routes.config";

import MessageCard from "@agir/front/genericComponents/MessageCard";
import PageFadeIn from "@agir/front/genericComponents/PageFadeIn";
import Panel from "@agir/front/genericComponents/Panel";
import { ResponsiveLayout } from "@agir/front/genericComponents/grid";

import MessageThreadMenu from "./MessageThreadMenu";

const StyledContent = styled.article`
  & > * {
    box-shadow: none;
    border: none;
    min-height: 100%;
    display: flex;
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
    border: none;
    border-radius: none;
    box-shadow: none;
  }

  & > * {
    flex: 1 1 auto;
    height: 100%;
    overflow-x: hidden;
    overflow-y: auto;
  }
`;

const DesktopThreadList = (props) => {
  const {
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

  useEffect(() => {
    // Autoselect first message on desktop
    !selectedMessagePk &&
      Array.isArray(messages) &&
      messages[0] &&
      onSelect(messages[0].id);
  }, [messages, selectedMessagePk, onSelect]);

  return (
    <StyledList>
      <MessageThreadMenu
        messages={messages}
        selectedMessageId={selectedMessage?.id}
        notificationSettingLink={notificationSettingLink}
        onSelect={onSelect}
        writeNewMessage={writeNewMessage}
      />
      <PageFadeIn ready={selectedMessagePk && selectedMessage}>
        {selectedMessage ? (
          <StyledContent>
            <MessageCard
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
                activeTab: "messages",
              })}
            />
          </StyledContent>
        ) : null}
      </PageFadeIn>
    </StyledList>
  );
};

const MobileThreadList = (props) => {
  const {
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

  return (
    <StyledList>
      <MessageThreadMenu
        messages={messages}
        selectedMessageId={selectedMessage?.id}
        notificationSettingLink={notificationSettingLink}
        onSelect={onSelect}
        writeNewMessage={writeNewMessage}
      />
      <Panel
        style={{ padding: "56px 0", background: "white" }}
        shouldShow={!!selectedMessage}
        noScroll
        isBehindTopBar
      >
        <PageFadeIn ready={selectedMessagePk && selectedMessage}>
          {selectedMessage && (
            <StyledContent>
              <MessageCard
                user={user}
                message={selectedMessage}
                comments={selectedMessage?.comments}
                onEdit={onEdit}
                onComment={onComment}
                onReport={onReport}
                onDelete={onDelete}
                onReportComment={onReportComment}
                onDeleteComment={onDeleteComment}
                isManager={selectedMessage?.group.isManager}
                groupURL={routeConfig.groupDetails.getLink({
                  groupPk: selectedMessage?.group.id,
                  activeTab: "messages",
                })}
                withMobileCommentField
              />
            </StyledContent>
          )}
        </PageFadeIn>
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
