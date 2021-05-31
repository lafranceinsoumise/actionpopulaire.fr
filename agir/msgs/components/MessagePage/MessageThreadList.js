import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

import { routeConfig } from "@agir/front/app/routes.config";

import Button from "@agir/front/genericComponents/Button";
import { Hide } from "@agir/front/genericComponents/grid";
import Link from "@agir/front/app/Link";
import MessageCard from "@agir/front/genericComponents/MessageCard";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";

import MessageThreadCard from "./MessageThreadCard";

const StyledNewMessageButton = styled.div`
  padding: 0.5rem 1.5rem 1.5rem;

  @media (max-width: ${style.collapse}px) {
    padding: 1.5rem;
    position: fixed;
    bottom: 80px;
    left: 0;
    right: 0;
    box-shadow: ${style.cardShadow};
  }
`;

const StyledMenu = styled.menu`
  padding: 0;
  margin: 0;
  width: 100%;
  text-align: center;

  header {
    padding: 0 1.5rem;
    height: 3.375rem;
    display: flex;
    align-items: center;
    justify-content: space-between;

    h2 {
      font-weight: 600;
      font-size: 1.125rem;
    }
  }

  ul {
    list-style: none;
    padding: 0;
    margin: 0;
  }
`;

const StyledContent = styled.article``;

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

  ${StyledMenu},
  ${StyledContent} {
    height: 100%;
    overflow-x: hidden;
    overflow-y: auto;
  }

  ${StyledMenu} {
    max-width: 400px;
    border-right: 1px solid ${style.black200};

    @media (max-width: ${style.collapse}px) {
      max-width: 100%;
      border-right: none;
    }
  }

  ${StyledContent} {
    & > * {
      border: none;
      min-height: 100%;
      display: flex;
    }
  }
`;

const MessageThreadList = (props) => {
  const {
    user,
    messages,
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
      <StyledMenu>
        <Hide under>
          <header>
            <h2>
              Messages{typeof writeNewMessage !== "function" ? " reçus" : ""}
            </h2>
            {notificationSettingLink && (
              <Link to={notificationSettingLink} style={{ lineHeight: 0 }}>
                <RawFeatherIcon
                  name="settings"
                  color={style.black1000}
                  width="1.5rem"
                  height="1.5rem"
                />
              </Link>
            )}
          </header>
        </Hide>
        {typeof writeNewMessage === "function" ? (
          <StyledNewMessageButton>
            <Button
              icon="edit"
              color="confirmed"
              onClick={writeNewMessage}
              style={{
                borderRadius: style.borderRadius,
                width: "100%",
                justifyContent: "center",
              }}
            >
              Nouveau message
            </Button>
          </StyledNewMessageButton>
        ) : null}
        <ul>
          {messages.map((message) => (
            <MessageThreadCard
              key={message.id}
              message={message}
              isSelected={selectedMessage && message.id === selectedMessage.id}
              onClick={onSelect}
            />
          ))}
        </ul>
      </StyledMenu>
      <Hide under>
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
      </Hide>
    </StyledList>
  );
};

MessageThreadList.propTypes = {
  messages: PropTypes.arrayOf(PropTypes.object),
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
