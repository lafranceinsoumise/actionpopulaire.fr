import PropTypes from "prop-types";
import React, { useState, useCallback } from "react";
import styled from "styled-components";

import Button from "@agir/front/genericComponents/Button";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";
import ShareLink from "@agir/front/genericComponents/ShareLink";
import Spacer from "@agir/front/genericComponents/Spacer";

import ModalShare from "@agir/front/genericComponents/ModalShare";
import ModalConfirmation from "@agir/front/genericComponents/ModalConfirmation";

const StyledWrapper = styled.div`
  display: flex;
  width: 100%;
  flex-flow: column nowrap;
  margin-top: 1rem;
`;

const StyledContainer = styled.div`
  display: flex;
  flex-align: row;
  justify-content: center;

  ${Button} {
    background-color: white;
    font-size: 14px;
    border: none;
    display: inline-flex;
    flex-direction: column;
    width: inherit;
  }
`;

const SecondaryActions = ({ id, isCertified, routes, contact }) => {
  const [isShareOpen, setIsShareOpen] = useState(false);
  const [isContactOpen, setIsContactOpen] = useState(false);

  const handleShareClose = useCallback(() => setIsShareOpen(false), []);
  const handleShareOpen = useCallback(() => setIsShareOpen(true), []);
  const handleContactClose = useCallback(() => setIsContactOpen(false), []);
  const handleContactOpen = useCallback(() => setIsContactOpen(true), []);

  return (
    <StyledWrapper>
      <StyledContainer>
        {contact?.email && (
          <Button type="button" onClick={handleContactOpen}>
            <RawFeatherIcon name="mail" width="1.5rem" height="1.5rem" />
            Contacter
          </Button>
        )}
        {isCertified && (
          <Button type="button" link route="donations" params={{ group: id }}>
            <RawFeatherIcon name="upload" width="1.5rem" height="1.5rem" />
            Financer
          </Button>
        )}
        <Button type="button" onClick={handleShareOpen}>
          <RawFeatherIcon name="share-2" width="1.5rem" height="1.5rem" />
          Partager
        </Button>
        <ModalShare
          shouldShow={isShareOpen}
          onClose={handleShareClose}
          url={routes.details}
        />
        <ModalConfirmation
          shouldShow={isContactOpen}
          onClose={handleContactClose}
          title="Contacter le groupe"
        >
          <p style={{ margin: "1rem 0" }}>
            Vous souhaitez rejoindre ce groupe ou bien recevoir des informations
            ? Envoyez un message aux animateur·ices de ce groupe d'action via
            leur e-mail&nbsp;:
            <Spacer size="1rem" />
            <ShareLink
              label="Copier"
              color="primary"
              url={contact?.email}
              $wrap
            />
          </p>
        </ModalConfirmation>
      </StyledContainer>
    </StyledWrapper>
  );
};

SecondaryActions.propTypes = {
  id: PropTypes.string.isRequired,
  isCertified: PropTypes.bool,
  routes: PropTypes.object,
  contact: PropTypes.shape({
    email: PropTypes.string,
  }),
};

export default SecondaryActions;
