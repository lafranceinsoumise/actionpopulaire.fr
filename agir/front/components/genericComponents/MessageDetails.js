import PropTypes from "prop-types";
import React, { useCallback, useState } from "react";

import style from "@agir/front/genericComponents/_variables.scss";
import styled from "styled-components";
import BottomSheet from "@agir/front/genericComponents/BottomSheet";
import ListUsers from "@agir/msgs/MessagePage/ListUsers";
import { ResponsiveLayout } from "@agir/front/genericComponents/grid";

import ModalConfirmation from "@agir/front/genericComponents/ModalConfirmation";

const Description = styled.span`
  font-size: 14px;
  cursor: pointer;

  @media (max-width: ${style.collapse}px) {
    font-size: 12px;
  }
`;

const PrimarySpan = styled.span`
  color: ${style.primary500};
`;

const MessageDetails = ({ message }) => {
  const [openParticipants, setOpenParticipants] = useState(false);

  const closeParticipants = useCallback(() => {
    setOpenParticipants(false);
  }, []);

  return (
    <>
      <Description onClick={() => setOpenParticipants(true)}>
        <PrimarySpan>{message?.participants.total} participant·es</PrimarySpan>{" "}
        - Membres de <PrimarySpan>{message?.group?.name}</PrimarySpan>
      </Description>

      <ResponsiveLayout
        DesktopLayout={ModalConfirmation}
        MobileLayout={BottomSheet}
        isOpen={openParticipants}
        shouldShow={openParticipants}
        onDismiss={closeParticipants}
        onClose={closeParticipants}
        shouldDismissOnClick
      >
        <ListUsers message={message} />
      </ResponsiveLayout>
    </>
  );
};

export default MessageDetails;
