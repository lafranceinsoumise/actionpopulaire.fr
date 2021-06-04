import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

import Button from "@agir/front/genericComponents/Button";
import { Hide } from "@agir/front/genericComponents/grid";
import Link from "@agir/front/app/Link";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";

import MessageThreadCard from "./MessageThreadCard";

const StyledNewMessageButton = styled.div`
  padding: 0.5rem 1.5rem 1.5rem;

  @media (max-width: ${style.collapse}px) {
    background-color: ${style.white};
    padding: 1.5rem;
    position: fixed;
    bottom: 72px;
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
  max-width: 400px;
  border-right: 1px solid ${style.black200};

  @media (max-width: ${style.collapse}px) {
    max-width: 100%;
    border-right: none;
    padding-bottom: 200px;
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
    notificationSettingLink,
    onSelect,
    writeNewMessage,
    ...rest
  } = props;

  return (
    <StyledMenu {...rest}>
      <Hide under>
        <header>
          <h2>
            Messages{typeof writeNewMessage !== "function" ? " reçus" : ""}
          </h2>
          {notificationSettingLink && (
            <Link
              to={notificationSettingLink}
              style={{ lineHeight: 0 }}
              disabled={isLoading}
            >
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
