import PropTypes from "prop-types";
import React from "react";
import { useLocation } from "react-router-dom";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

import Button from "@agir/front/genericComponents/Button";
import { Hide } from "@agir/front/genericComponents/grid";
import NotificationSettingLink from "@agir/activity/NotificationSettings/NotificationSettingLink";

import MessageThreadCard from "./MessageThreadCard";

const StyledNewMessageButton = styled.div`
  padding: 0.5rem 1.5rem 1.5rem;

  @media (max-width: ${style.collapse}px) {
    background-color: ${style.white};
    padding: 1rem;
    position: fixed;
    bottom: 72px;
    left: 0;
    right: 0;
    box-shadow: ${style.cardShadow};
    z-index: 1;
  }
`;

const StyledMenu = styled.menu`
  padding: 0;
  margin: 0;
  width: 100%;
  text-align: center;
  max-width: 400px;
  border-right: 1px solid ${style.black200};

  @media (max-width: ${style.collapse}px) {
    max-width: 100%;
    border-right: none;
    padding-bottom: 160px;
    isolation: isolate;
  }

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

const MessageThreadMenu = (props) => {
  const {
    isLoading,
    messages,
    selectedMessageId,
    onSelect,
    writeNewMessage,
    ...rest
  } = props;

  const { pathname } = useLocation();
  const settingsRoot = pathname ? pathname.slice(1, -1) : "messages";

  return (
    <StyledMenu {...rest}>
      <Hide under>
        <header>
          <h2>
            Messages{typeof writeNewMessage !== "function" ? " reçus" : ""}
          </h2>
          <NotificationSettingLink root={settingsRoot} iconLink />
        </header>
      </Hide>
      {typeof writeNewMessage === "function" ? (
        <StyledNewMessageButton>
          <Button
            icon="edit"
            color="confirmed"
            onClick={writeNewMessage}
            disabled={isLoading}
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
            isSelected={message.id === selectedMessageId}
            onClick={onSelect}
            disabled={isLoading}
          />
        ))}
      </ul>
    </StyledMenu>
  );
};

MessageThreadMenu.propTypes = {
  isLoading: PropTypes.bool,
  messages: PropTypes.arrayOf(PropTypes.object),
  selectedMessageId: PropTypes.string,
  notificationSettingLink: PropTypes.string,
  onSelect: PropTypes.func,
  writeNewMessage: PropTypes.func,
};

export default MessageThreadMenu;
