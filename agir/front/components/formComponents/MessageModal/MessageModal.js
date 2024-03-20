import PropTypes from "prop-types";
import React, { useCallback, useMemo, useState } from "react";

import Trigger from "./Trigger";
import Modal from "./Modal";

const MessageModal = (props) => {
  const {
    user,
    message,
    onSend,
    onDismiss,
    groups,
    events,
    loadMoreEvents,
    onSelectGroup,
    isLoading,
    errors,
  } = props;

  const messageId = message?.id;

  const [isOpen, setIsOpen] = useState(false);

  const handleOpen = useCallback(() => {
    setIsOpen(true);
  }, []);

  const handleClose = useCallback(() => {
    setIsOpen(false);
    onDismiss && onDismiss();
  }, [onDismiss]);

  useMemo(() => {
    messageId ? handleOpen() : handleClose();
  }, [messageId, handleOpen, handleClose]);

  return (
    <>
      <Trigger user={user} onClick={handleOpen} />
      <Modal
        shouldShow={isOpen}
        onClose={handleClose}
        user={user}
        groups={groups}
        events={events}
        loadMoreEvents={loadMoreEvents}
        onSelectGroup={onSelectGroup}
        isLoading={isLoading}
        message={message}
        onSend={onSend}
        errors={errors}
      />
    </>
  );
};
MessageModal.propTypes = {
  groups: PropTypes.arrayOf(PropTypes.object),
  events: PropTypes.arrayOf(PropTypes.object),
  selectedEvent: PropTypes.object,
  loadMoreEvents: PropTypes.func,
  onSelectGroup: PropTypes.func,
  messageId: PropTypes.string,
  message: PropTypes.shape({
    id: PropTypes.string.isRequired,
    text: PropTypes.string,
    linkedEvent: PropTypes.object,
    group: PropTypes.object,
  }),
  onSend: PropTypes.func.isRequired,
  onDismiss: PropTypes.func,
  user: PropTypes.object,
  isLoading: PropTypes.bool,
  errors: PropTypes.object,
};
export default MessageModal;
