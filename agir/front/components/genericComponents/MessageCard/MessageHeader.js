import PropTypes from "prop-types";
import React, { useState } from "react";
import styled from "styled-components";

import ButtonLockMessage from "@agir/front/genericComponents/ButtonLockMessage";
import ButtonMuteMessage from "@agir/front/genericComponents/ButtonMuteMessage";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";
import MessageDetails from "@agir/front/genericComponents/MessageDetails";
import ModalConfirmation from "@agir/front/genericComponents/ModalConfirmation";
import Spacer from "@agir/front/genericComponents/Spacer";

const StyledSubject = styled.h2`
  font-size: 1.125rem;
  line-height: 1.5;
  font-weight: 600;
  margin: 0;
  display: inline-flex;
  align-items: center;

  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  display: block;
  cursor: pointer;

  @media (max-width: ${(props) => props.theme.collapse}px) {
    white-space: normal;
    cursor: default;
  }

  @media (min-width: ${(props) => props.theme.collapse}px) {
    max-width: 360px;
  }
  @media (min-width: 1300px) {
    max-width: 560px;
  }

  ${RawFeatherIcon} {
    background-color: #eeeeee;
    border-radius: 2rem;
    padding: 8px;
    margin-right: 0.5rem;
  }
`;

const StyledMessageHeader = styled.div`
  height: 80px;
  padding: 1rem;
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  border: 1px solid ${(props) => props.theme.text100};
  border-bottom: none;
  background-color: ${(props) => props.theme.background0};

  @media (max-width: ${(props) => props.theme.collapse}px) {
    padding: 0;
    padding-top: 0.5rem;
    padding-bottom: 0.5rem;
    height: unset;
    border: none;
  }
`;

const MessageReadonlyHeader = ({ message, subject }) => {
  return (
    <StyledMessageHeader>
      <div style={{ display: "flex" }}>
        <RawFeatherIcon name="mail" style={{ marginRight: "1rem" }} />
        <div
          style={{
            display: "flex",
            flexDirection: "column",
          }}
        >
          <StyledSubject>{subject}</StyledSubject>
          <MessageDetails message={message} />
        </div>
      </div>
    </StyledMessageHeader>
  );
};
MessageReadonlyHeader.propTypes = {
  message: PropTypes.shape({
    text: PropTypes.string.isRequired,
    readonly: PropTypes.bool,
  }),
  subject: PropTypes.string.isRequired,
};

const MessageHeader = (props) => {
  const { message, subject, isManager, isAuthor, readOnly } = props;

  const [isModalOpen, setIsModalOpen] = useState(false);

  const showModal = () => {
    setIsModalOpen(true);
  };

  if (readOnly || message?.readonly) {
    return <MessageReadonlyHeader message={message} subject={subject} />;
  }

  return (
    <StyledMessageHeader>
      <div style={{ display: "flex" }}>
        <RawFeatherIcon name="mail" style={{ marginRight: "1rem" }} />
        <div
          style={{
            display: "flex",
            flexDirection: "column",
          }}
        >
          <StyledSubject onClick={showModal}>{subject}</StyledSubject>
          <MessageDetails message={message} />
        </div>
      </div>
      <div>
        {(isManager || isAuthor) && <ButtonLockMessage message={message} />}
        <Spacer size="0.5rem" style={{ display: "inline-block" }} />
        {<ButtonMuteMessage message={message} />}
      </div>
      <ModalConfirmation
        shouldShow={isModalOpen}
        shouldDismissOnClick={false}
        onClose={() => setIsModalOpen(false)}
      >
        <h3>{subject}</h3>
      </ModalConfirmation>
    </StyledMessageHeader>
  );
};
MessageHeader.propTypes = {
  message: PropTypes.shape({
    text: PropTypes.string.isRequired,
    readonly: PropTypes.bool,
  }),
  subject: PropTypes.string.isRequired,
  isManager: PropTypes.bool,
  isAuthor: PropTypes.bool,
  readOnly: PropTypes.bool,
};

export default MessageHeader;
