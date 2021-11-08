import PropTypes from "prop-types";
import React, { useState, useCallback } from "react";
import styled from "styled-components";
import style from "@agir/front/genericComponents/_variables.scss";

import Link from "@agir/front/app/Link";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";
import ShareLink from "@agir/front/genericComponents/ShareLink";
import Spacer from "@agir/front/genericComponents/Spacer";

import ModalConfirmation from "@agir/front/genericComponents/ModalConfirmation";
import ShareContentUrl from "@agir/front/genericComponents/ShareContentUrl";

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

const SecondaryActions = ({ id, isCertified, routes, contact }) => {
  const [isShareOpen, setIsShareOpen] = useState(false);
  const [isContactOpen, setIsContactOpen] = useState(false);

  const handleShareClose = useCallback(() => setIsShareOpen(false), []);
  const handleShareOpen = useCallback(() => setIsShareOpen(true), []);
  const handleContactClose = useCallback(() => setIsContactOpen(false), []);
  const handleContactOpen = useCallback(() => setIsContactOpen(true), []);

  return (
    <StyledContainer>
      {contact?.email && (
        <button type="button" onClick={handleContactOpen}>
          <RawFeatherIcon name="mail" width="1.5rem" height="1.5rem" />
          <span>Contacter</span>
        </button>
      )}
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

      <ModalConfirmation
        shouldShow={isContactOpen}
        onClose={handleContactClose}
        title="Contacter le groupe"
      >
        <p style={{ margin: "1rem 0" }}>
          Vous souhaitez rejoindre ce groupe ou bien recevoir des informations ?
          Envoyez un message aux animateur·ices de ce groupe d'action via leur
          e-mail&nbsp;:
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
