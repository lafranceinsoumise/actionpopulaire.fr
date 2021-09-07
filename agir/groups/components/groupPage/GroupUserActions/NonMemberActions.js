import PropTypes from "prop-types";
import React, { useState, useCallback } from "react";
import styled from "styled-components";

import Button from "@agir/front/genericComponents/Button";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";
import Spacer from "@agir/front/genericComponents/Spacer";

import ModalShare from "@agir/front/genericComponents/ModalShare";

const StyledWrapper = styled.div`
  display: flex;
  width: 100%;
  flex-flow: column nowrap;
  gap: 0.5rem;

  ${Button} {
    ${"" /* TODO: remove after Button refactoring merge */}
    width: 100%;
    margin: 0;
    justify-content: center;
  }

  p {
    margin: 0.5rem 0 0;
    text-align: center;
    font-size: 0.688rem;
    font-weight: 400;
    line-height: 1.5;
    color: ${(props) => props.theme.black700};
  }
`;

const StyledContainer = styled.div`
  display: flex;
  flex-align: row;
  justify-content: center;

  ${Button} {
    background-color: white;
    font-size: 12px;
    border: none;
    display: inline-flex;
    flex-direction: column;
    width: inherit;
  }
`;

const NonMemberActions = (props) => {
  const { onJoin, onFollow, isLoading, routes } = props;

  const [isOpen, setIsOpen] = useState(false);

  const handleClose = useCallback(() => setIsOpen(false), []);
  const handleShare = useCallback(() => setIsOpen(true), []);

  return (
    <StyledWrapper>
      <Button
        type="button"
        color="success"
        disabled={isLoading}
        onClick={onJoin}
      >
        <RawFeatherIcon name="user-plus" width="1.5rem" height="1.5rem" />
        <Spacer size="10px" />
        Rejoindre
      </Button>
      <Button type="button" disabled={isLoading} onClick={onFollow}>
        <RawFeatherIcon name="plus" width="1.5rem" height="1.5rem" />
        <Spacer size="10px" />
        Suivre
      </Button>

      <StyledContainer>
        <Button type="button">
          <RawFeatherIcon name="mail" width="1rem" height="1rem" />
          Contacter
        </Button>
        {!!routes?.donations && (
          <Button type="button" link route={routes.donations}>
            <RawFeatherIcon name="upload" width="1rem" height="1rem" />
            Financer
          </Button>
        )}
        <Button type="button" onClick={handleShare}>
          <RawFeatherIcon name="share-2" width="1rem" height="1rem" />
          Partager
        </Button>
      </StyledContainer>

      <ModalShare
        shouldShow={isOpen}
        onClose={handleClose}
        url={routes.details}
      />
    </StyledWrapper>
  );
};
NonMemberActions.propTypes = {
  onJoin: PropTypes.func,
  onFollow: PropTypes.func,
  isLoading: PropTypes.bool,
};
export default NonMemberActions;
