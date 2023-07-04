import PropTypes from "prop-types";
import React, { useCallback, useMemo, useState } from "react";
import { useHistory, useLocation } from "react-router-dom";

import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";

import { getUser } from "@agir/front/globalContext/reducers";
import * as groupAPI from "@agir/groups/utils/api";
import { routeConfig } from "@agir/front/app/routes.config";
import { useSelectMessage } from "@agir/msgs/common/hooks";
import { useSelector } from "@agir/front/globalContext/GlobalContext";

import Button from "@agir/front/genericComponents/Button";
import MessageModal from "@agir/front/formComponents/MessageModal/Modal";
import ModalConfirmation from "@agir/front/genericComponents/ModalConfirmation";
import ShareLink from "@agir/front/genericComponents/ShareLink";
import Spacer from "@agir/front/genericComponents/Spacer";

const ContactButton = (props) => {
  const { id, isMessagingEnabled, contact, buttonTrigger = false } = props;

  const user = useSelector(getUser);
  const hasModal = !isMessagingEnabled && !contact?.email;
  const history = useHistory();
  const location = useLocation();

  const urlParams = useMemo(
    () => new URLSearchParams(location.search),
    [location]
  );
  const hasMessage = !!user && !!urlParams.get("contact", false);

  const onSelectMessage = useSelectMessage();
  const [messageModalOpen, setMessageModalOpen] = useState(hasMessage);

  const redirectToLogin = useCallback(() => {
    urlParams.set("contact", 1);
    history.push(routeConfig.login.getLink(), {
      ...(location.state || {}),
      from: "groupDetails",
      next: `${location.pathname}?${urlParams.toString()}`,
    });
  }, [location, urlParams, history]);

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

  if (hasModal) {
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
          onClick={user ? handleMessageOpen : redirectToLogin}
        >
          Contacter
        </Button>
      ) : (
        <button
          type="button"
          onClick={user ? handleMessageOpen : redirectToLogin}
        >
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
