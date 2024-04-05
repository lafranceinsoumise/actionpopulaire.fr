import PropTypes from "prop-types";
import React, { useCallback, useEffect, useMemo, useState } from "react";
import styled from "styled-components";

import * as style from "@agir/front/genericComponents/_variables.scss";

import Button from "@agir/front/genericComponents/Button";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";
import ModalWrapper from "@agir/front/genericComponents/Modal";
import { useFileInput } from "@agir/front/formComponents/MessageAttachment";
import GroupStep from "./GroupStep";
import EventStep from "./EventStep";
import MessageStep from "./MessageStep";

const EMPTY_EVENTS = [
  {
    id: null,
    name: "Ne concerne pas un événement",
    type: "NULL",
  },
  {
    id: null,
    name: "Événement futur",
  },
];

const SUBJECT_MAX_LENGTH = 150;
const TEXT_MAX_LENGTH = 3000;

const StyledIconButton = styled.button`
  display: flex;
  align-items: center;
  justify-content: center;
  height: 2rem;
  width: 2rem;
  border: none;
  padding: 0;
  margin: 0;
  text-decoration: none;
  background: inherit;
  cursor: pointer;
  text-align: center;
  -webkit-appearance: none;
  -moz-appearance: none;
  color: ${style.black1000};

  &:last-child {
    justify-content: flex-end;
  }
  &:first-child {
    justify-content: flex-start;
  }
`;
const StyledModalHeader = styled.header`
  display: ${({ $mobile }) => ($mobile ? "none" : "grid")};
  grid-template-columns: 1fr auto;
  align-items: center;
  padding: 0 1.5rem;
  height: 54px;

  @media (max-width: ${style.collapse}px) {
    display: ${({ $mobile }) => ($mobile ? "flex" : "none")};
    align-items: center;
    height: 4rem;
    padding: 0 1rem;
    gap: 0.5rem;
    position: sticky;
    top: 0;
    background-color: white;
    z-index: 1;
  }

  & > * {
    @media (max-width: ${style.collapse}px) {
      flex: 0 0 auto;
    }
  }

  h4 {
    grid-column: 1/3;
    grid-row: 1/2;
    text-align: center;
    font-weight: 500;
    font-size: 1rem;
  }

  ${StyledIconButton} {
    grid-column: 2/3;
    grid-row: 1/2;

    @media (max-width: ${style.collapse}px) {
      margin-right: auto;
    }
  }
`;
const StyledModalBody = styled.div`
  padding: 0;
  min-height: 200px;
`;
const StyledModalFooter = styled.footer`
  padding: 0 1rem 1rem;

  @media (max-width: ${style.collapse}px) {
    display: none;
  }

  ${Button} {
    width: 100%;
  }
`;
const StyledModalContent = styled.div`
  max-width: 600px;
  margin: 40px auto;
  background-color: white;
  border-radius: ${style.borderRadius};

  @media (max-width: ${style.collapse}px) {
    border-radius: 0;
    max-width: 100%;
    min-height: 100vh;
    padding-bottom: 1.5rem;
    margin: 0;
    display: flex;
    flex-flow: column nowrap;
  }

  ${StyledModalHeader} {
    border-bottom: ${({ $isLoading }) =>
      $isLoading
        ? `8px solid ${style.secondary500}`
        : `1px solid ${style.black100};`};
    transition: border-bottom 250ms ease-in-out;
  }
  ${StyledModalBody},
  ${StyledModalFooter} {
    opacity: ${({ $isLoading }) => ($isLoading ? ".3" : "1")};
    transition: opacity 250ms ease-in-out;
  }
  ${StyledModalBody} {
    @media (max-width: ${style.collapse}px) {
      flex: 1 1 auto;
    }
  }
`;

const Modal = (props) => {
  const {
    shouldShow,
    onClose,
    groups,
    events,
    onSend,
    user,
    isLoading,
    loadMoreEvents,
    message,
    onSelectGroup,
    groupPk,
    onBoarding,
    errors,
  } = props;

  const initialMessage = useMemo(() => {
    if (!message || !message.id || !!message.linkedEvent) {
      return message;
    }
    return {
      ...message,
      linkedEvent: EMPTY_EVENTS[0],
    };
  }, [message]);

  const [subject, setSubject] = useState(message?.subject || "");
  const [text, setText] = useState(message?.text || "");
  const [attachment, setAttachment] = useState(message?.attachment || null);
  const [handleClearAttachment, handleAttach, attachmentInput] =
    useFileInput(setAttachment);

  const [hasBackButton, setHasBackButton] = useState(false);
  const [selectedEvent, setSelectedEvent] = useState(
    (message && message.linkedEvent) || null,
  );
  const [selectedGroup, setSelectedGroup] = useState(message?.group || null);

  const maySend = useMemo(() => {
    if (isLoading) {
      return false;
    }
    if (!selectedEvent) {
      return true;
    }
    if (Array.isArray(groups)) {
      return !!selectedGroup;
    }
    return true;
  }, [isLoading, groups, selectedEvent, selectedGroup]);

  const eventOptions = useMemo(() => {
    if (!Array.isArray(events) || events.length === 0) {
      return [...EMPTY_EVENTS];
    }
    return [...EMPTY_EVENTS, ...events];
  }, [events]);

  const handleChangeMessage = useCallback((prop, text) => {
    if (prop === "subject") {
      setSubject(text);
    } else {
      setText(text);
    }
  }, []);

  const handleSelectEvent = useCallback((event) => {
    setSelectedEvent(event);
    setHasBackButton(true);
  }, []);

  const handleSelectGroup = useCallback(
    (group) => {
      setSelectedGroup(group);
      onSelectGroup && onSelectGroup(group);
    },
    [onSelectGroup],
  );

  const handleClearEvent = useCallback(() => {
    setSelectedEvent(null);
    setHasBackButton(false);
  }, []);

  const handleSend = useCallback(() => {
    maySend &&
      onSend({
        ...(initialMessage || {}),
        attachment,
        subject: subject.trim(),
        text: text.trim(),
        linkedEvent: selectedEvent,
        group: selectedGroup,
      });
  }, [
    maySend,
    onSend,
    initialMessage,
    subject,
    text,
    attachment,
    selectedEvent,
    selectedGroup,
  ]);

  const handleSendOnCtrlEnter = useCallback(
    (e) => {
      if (maySend && e.ctrlKey && e.keyCode === 13) {
        handleSend();
      }
    },
    [maySend, handleSend],
  );

  useEffect(() => {
    if (shouldShow) {
      setSubject(initialMessage?.subject || "");
      setText(initialMessage?.text || "");
      setAttachment(initialMessage?.attachment || null);
      setSelectedEvent(initialMessage?.linkedEvent || null);
      setSelectedGroup(initialMessage?.group || null);
      setHasBackButton(false);
    }
  }, [shouldShow, initialMessage]);

  return (
    <ModalWrapper shouldShow={shouldShow} noScroll>
      <StyledModalContent $isLoading={isLoading}>
        <StyledModalHeader>
          <h4>Nouveau message</h4>
          <StyledIconButton onClick={onClose} disabled={isLoading}>
            <RawFeatherIcon name="x" />
          </StyledIconButton>
        </StyledModalHeader>
        <StyledModalHeader $mobile>
          <StyledIconButton
            onClick={hasBackButton ? handleClearEvent : onClose}
            disabled={isLoading}
          >
            <RawFeatherIcon name={hasBackButton ? "arrow-left" : "x"} />
          </StyledIconButton>
          {(selectedEvent || !!groupPk) && (
            <>
              <Button
                small
                icon="paperclip"
                color="choose"
                onClick={handleAttach}
              >
                Joindre
              </Button>
              {attachmentInput}
              <Button
                color="secondary"
                small
                disabled={!maySend}
                onClick={handleSend}
              >
                Envoyer
              </Button>
            </>
          )}
        </StyledModalHeader>
        <StyledModalBody onKeyDown={handleSendOnCtrlEnter}>
          {Array.isArray(groups) && !selectedGroup ? (
            <GroupStep groups={groups} onSelectGroup={handleSelectGroup} />
          ) : !selectedEvent && !groupPk ? (
            <EventStep
              events={eventOptions}
              onSelectEvent={handleSelectEvent}
              loadMoreEvents={loadMoreEvents}
              hasEmailWarning={!message || !message.id}
            />
          ) : (
            <MessageStep
              text={text}
              subject={subject}
              event={selectedEvent}
              attachment={attachment}
              user={user}
              onChange={handleChangeMessage}
              onClearEvent={handleClearEvent}
              onAttach={handleAttach}
              onClearAttachment={handleClearAttachment}
              disabled={isLoading}
              errors={errors}
              maxLength={TEXT_MAX_LENGTH}
              subjectmaxLength={SUBJECT_MAX_LENGTH}
              groupPk={groupPk}
              onBoarding={onBoarding}
            />
          )}
        </StyledModalBody>
        {(selectedEvent || !!groupPk) && (
          <StyledModalFooter>
            <Button color="secondary" disabled={!maySend} onClick={handleSend}>
              Envoyer le message
            </Button>
          </StyledModalFooter>
        )}
      </StyledModalContent>
    </ModalWrapper>
  );
};
Modal.propTypes = {
  shouldShow: PropTypes.bool,
  onClose: PropTypes.func,
  groups: PropTypes.arrayOf(PropTypes.object),
  events: PropTypes.arrayOf(PropTypes.object),
  selectedEvent: PropTypes.object,
  loadMoreEvents: PropTypes.func,
  onSelectGroup: PropTypes.func,
  message: PropTypes.shape({
    id: PropTypes.string,
    subject: PropTypes.string,
    text: PropTypes.string,
    linkedEvent: PropTypes.object,
    group: PropTypes.object,
    attachment: PropTypes.object,
  }),
  onSend: PropTypes.func.isRequired,
  user: PropTypes.object,
  isLoading: PropTypes.bool,
  groupPk: PropTypes.string,
  onBoarding: PropTypes.bool,
  errors: PropTypes.object,
};
export default Modal;
