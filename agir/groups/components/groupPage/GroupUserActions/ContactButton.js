import PropTypes from "prop-types";
import React, { useState, useCallback } from "react";

import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";

import { useSelector } from "@agir/front/globalContext/GlobalContext";
import { getUser } from "@agir/front/globalContext/reducers";
import ModalConfirmation from "@agir/front/genericComponents/ModalConfirmation";
import ShareLink from "@agir/front/genericComponents/ShareLink";
import Spacer from "@agir/front/genericComponents/Spacer";

import MessageModal from "@agir/front/formComponents/MessageModal/Modal";
import { useSelectMessage } from "@agir/msgs/common/hooks";
import * as groupAPI from "@agir/groups/utils/api";
import Button from "@agir/front/genericComponents/Button";

const ContactButton = (props) => {
  const { id, isMessagingEnabled, contact, buttonTrigger = false } = props;

  const user = useSelector(getUser);
  const onSelectMessage = useSelectMessage();
  const [messageModalOpen, setMessageModalOpen] = useState(false);

  const handleMessageClose = useCallback(() => setMessageModalOpen(false), []);
  const handleMessageOpen = useCallback(() => setMessageModalOpen(true), []);

  const sendPrivateMessage = async (msg) => {
    const message = {
      subject: msg.subject,
      text: msg.text,
    };
    const result = await groupAPI.createPrivateMessage(id, message);
    onSelectMessage(result.data?.id);
  };

  if (!isMessagingEnabled && !contact?.email) {
    return null;
  }

  return (
    <>
      {buttonTrigger ? (
        <Button
          inline
          small
          color="primary"
          icon="mail"
          onClick={handleMessageOpen}
        >
          Contacter
        </Button>
      ) : (
        <button type="button" onClick={handleMessageOpen}>
          <RawFeatherIcon name="mail" width="1.5rem" height="1.5rem" />
          <span>Contacter</span>
        </button>
      )}
      {isMessagingEnabled ? (
        <MessageModal
          shouldShow={messageModalOpen}
          user={user}
          groupPk={id}
          onSend={sendPrivateMessage}
          onClose={handleMessageClose}
        />
      ) : (
        <ModalConfirmation
          shouldShow={messageModalOpen}
          onClose={handleMessageClose}
          title="Contactez les animateur·ices du groupe"
        >
          <div>
            Vous pouvez contacter les animateur·ices du groupe par e-mail&nbsp;:
            <Spacer size="1rem" />
            <ShareLink
              label="Copier"
              color="primary"
              url={contact?.email}
              $wrap
            />
          </div>
        </ModalConfirmation>
      )}
    </>
  );
};

ContactButton.propTypes = {
  id: PropTypes.string.isRequired,
  isMessagingEnabled: PropTypes.bool,
  contact: PropTypes.object,
  buttonTrigger: PropTypes.bool,
};

export default ContactButton;
