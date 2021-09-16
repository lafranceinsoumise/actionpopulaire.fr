import PropTypes from "prop-types";
import React, { useState, useCallback } from "react";
import styled from "styled-components";

import Button from "@agir/front/genericComponents/Button";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";

import ModalShare from "@agir/front/genericComponents/ModalShare";

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

const SecondaryActions = ({ routes, contact }) => {
  const [isOpen, setIsOpen] = useState(false);

  const handleClose = useCallback(() => setIsOpen(false), []);
  const handleShare = useCallback(() => setIsOpen(true), []);

  return (
    <StyledWrapper>
      <StyledContainer>
        {contact?.email && (
          <a href={`mailto:${contact.email}`}>
            <Button type="button">
              <RawFeatherIcon name="mail" width="1.5rem" height="1.5rem" />
              Contacter
            </Button>
          </a>
        )}
        {!!routes?.donations && (
          <Button type="button" link route={routes.donations}>
            <RawFeatherIcon name="upload" width="1.5rem" height="1.5rem" />
            Financer
          </Button>
        )}
        <Button type="button" onClick={handleShare}>
          <RawFeatherIcon name="share-2" width="1.5rem" height="1.5rem" />
          Partager
        </Button>
        <ModalShare
          shouldShow={isOpen}
          onClose={handleClose}
          url={routes.details}
        />
      </StyledContainer>
    </StyledWrapper>
  );
};

SecondaryActions.propTypes = {
  routes: PropTypes.object,
  contact: PropTypes.shape({
    email: PropTypes.string,
  }),
};

export default SecondaryActions;
