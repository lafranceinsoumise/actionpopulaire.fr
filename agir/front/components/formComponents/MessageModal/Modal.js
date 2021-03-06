import PropTypes from "prop-types";
import React, { useCallback, useEffect, useMemo, useState } from "react";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

import Button from "@agir/front/genericComponents/Button";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";
import ModalWrapper from "@agir/front/genericComponents/Modal";

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
    justify-content: space-between;
    height: 64px;
    padding: 0 1rem;
    position: sticky;
    top: 0;
    background-color: white;
    z-index: 1;
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
    justify-content: center;
  }
`;
const StyledModalContent = styled.div`
  max-width: 600px;
  margin: 40px auto;
  background-color: white;
  border-radius: 8px;

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
    events,
    onSend,
    user,
    isLoading,
    loadMoreEvents,
    message,
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

  const [text, setText] = useState((message && message.text) || "");
  const [hasBackButton, setHasBackButton] = useState(false);
  const [selectedEvent, setSelectedEvent] = useState(
    (message && message.linkedEvent) || null
  );

  const maySend =
    !isLoading && selectedEvent && text && text.trim().length <= 2000;

  const handleChangeText = useCallback((text) => {
    setText(text);
  }, []);

  const handleSelectEvent = useCallback((event) => {
    setSelectedEvent(event);
    setHasBackButton(true);
  }, []);

  const handleClearEvent = useCallback(() => {
    setSelectedEvent(null);
    setHasBackButton(false);
  }, []);

  const handleSend = useCallback(() => {
    maySend &&
      onSend({
        ...(initialMessage || {}),
        text: text.trim(),
        linkedEvent: selectedEvent,
      });
  }, [maySend, onSend, initialMessage, text, selectedEvent]);

  useEffect(() => {
    if (shouldShow) {
      setText((initialMessage && initialMessage.text) || "");
      setSelectedEvent((initialMessage && initialMessage.linkedEvent) || null);
      setHasBackButton(false);
    }
  }, [shouldShow, initialMessage]);

  const handleSendOnCtrlEnter = useCallback(
    (e) => {
      if (maySend && e.ctrlKey && e.keyCode === 13) {
        handleSend();
      }
    },
    [maySend, handleSend]
  );

  const eventOptions = useMemo(
    () =>
      Array.isArray(events) && events.length > 0
        ? [...EMPTY_EVENTS, ...events]
        : [...EMPTY_EVENTS],
    [events]
  );

  return (
    <ModalWrapper
      shouldShow={shouldShow}
      onClose={isLoading ? undefined : onClose}
      noScroll
    >
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
          {selectedEvent ? (
            <Button
              color="secondary"
              small
              disabled={!maySend}
              onClick={handleSend}
            >
              Publier
            </Button>
          ) : null}
        </StyledModalHeader>
        <StyledModalBody onKeyDown={handleSendOnCtrlEnter}>
          {selectedEvent ? (
            <MessageStep
              text={text}
              event={selectedEvent}
              user={user}
              onChange={handleChangeText}
              onClearEvent={handleClearEvent}
              disabled={isLoading}
              maxLength={2000}
            />
          ) : (
            <EventStep
              events={eventOptions}
              onSelectEvent={handleSelectEvent}
              loadMoreEvents={loadMoreEvents}
              hasEmailWarning={!message || !message.id}
            />
          )}
        </StyledModalBody>
        {selectedEvent ? (
          <StyledModalFooter>
            <Button color="secondary" disabled={!maySend} onClick={handleSend}>
              Publier le message
            </Button>
          </StyledModalFooter>
        ) : null}
      </StyledModalContent>
    </ModalWrapper>
  );
};
Modal.propTypes = {
  shouldShow: PropTypes.bool,
  onClose: PropTypes.func,
  events: PropTypes.arrayOf(PropTypes.object),
  selectedEvent: PropTypes.object,
  loadMoreEvents: PropTypes.func,
  message: PropTypes.shape({
    id: PropTypes.string,
    text: PropTypes.string,
    linkedEvent: PropTypes.object,
  }),
  onSend: PropTypes.func.isRequired,
  user: PropTypes.object,
  isLoading: PropTypes.bool,
};
export default Modal;
