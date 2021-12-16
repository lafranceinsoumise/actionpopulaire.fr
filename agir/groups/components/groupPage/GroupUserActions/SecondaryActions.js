import PropTypes from "prop-types";
import React, { useState, useCallback } from "react";
import styled from "styled-components";
import style from "@agir/front/genericComponents/_variables.scss";

import Link from "@agir/front/app/Link";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";

import { useSelector } from "@agir/front/globalContext/GlobalContext";
import { getUser } from "@agir/front/globalContext/reducers";
import ModalConfirmation from "@agir/front/genericComponents/ModalConfirmation";
import ShareContentUrl from "@agir/front/genericComponents/ShareContentUrl";

import MessageModal from "@agir/front/formComponents/MessageModal/Modal";
import { useSelectMessage } from "@agir/msgs/common/hooks";
import * as groupAPI from "@agir/groups/api";

const StyledLink = styled(Link)``;
const StyledContainer = styled.div`
  margin-top: 1rem;
  display: flex;
  gap: 0.75rem;
  justify-content: center;
  width: 100%;

  button,
  ${StyledLink} {
    cursor: pointer;
    flex: 0 1 auto;
    min-width: 1px;
    padding: 0.75rem;
    background-color: transparent;
    color: ${style.black1000};
    border: none;
    text-align: center;
    font-size: 0.875rem;
    font-weight: 500;

    &:hover,
    &:focus {
      text-decoration: underline;
    }

    & > span {
      display: block;
      white-space: nowrap;
      text-overflow: ellipsis;
      overflow: hidden;
    }
  }
`;

const SecondaryActions = ({ id, isCertified, routes }) => {
  const user = useSelector(getUser);
  const onSelectMessage = useSelectMessage();

  const [isShareOpen, setIsShareOpen] = useState(false);
  const [messageModalOpen, setMessageModalOpen] = useState(false);

  const handleShareClose = useCallback(() => setIsShareOpen(false), []);
  const handleShareOpen = useCallback(() => setIsShareOpen(true), []);

  const handleMessageClose = useCallback(() => setMessageModalOpen(false), []);
  const handleMessageOpen = useCallback(() => setMessageModalOpen(true), []);

  const sendPrivateMessage = async (msg) => {
    const message = {
      subject: msg.subject,
      text: msg.text,
    };
    const result = await groupAPI.createPrivateMessage(id, message);
    onSelectMessage(result.data.id);
  };

  return (
    <StyledContainer>
      <button type="button" onClick={handleMessageOpen}>
        <RawFeatherIcon name="mail" width="1.5rem" height="1.5rem" />
        <span>Contacter</span>
      </button>
      {isCertified && (
        <StyledLink route="donations" params={{ group: id }}>
          <RawFeatherIcon name="upload" width="1.5rem" height="1.5rem" />
          <span>Financer</span>
        </StyledLink>
      )}
      <button type="button" onClick={handleShareOpen}>
        <RawFeatherIcon name="share-2" width="1.5rem" height="1.5rem" />
        <span>Partager</span>
      </button>
      <ModalConfirmation
        shouldShow={isShareOpen}
        onClose={handleShareClose}
        title="Partager le groupe"
      >
        <ShareContentUrl url={routes.details} />
      </ModalConfirmation>
      <MessageModal
        shouldShow={messageModalOpen}
        user={user}
        groupPk={id}
        onSend={sendPrivateMessage}
        onClose={handleMessageClose}
      />
    </StyledContainer>
  );
};

SecondaryActions.propTypes = {
  id: PropTypes.string.isRequired,
  isCertified: PropTypes.bool,
  routes: PropTypes.object,
};

export default SecondaryActions;
