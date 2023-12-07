import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import Button from "@agir/front/genericComponents/Button";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";
import Spacer from "@agir/front/genericComponents/Spacer";

const StyledWrapper = styled.div`
  display: flex;
  width: 100%;
  flex-flow: column nowrap;
  gap: 0.5rem;

  p {
    margin: 0.5rem 0 0;
    text-align: center;
    font-size: 0.688rem;
    font-weight: 400;
    line-height: 1.5;
    color: ${(props) => props.theme.black700};
  }
`;

const NonMemberActions = (props) => {
  const { onJoin, onFollow, isOpen, isLoading } = props;
  return (
    <StyledWrapper>
      <Button
        type="button"
        color="success"
        disabled={!isOpen || isLoading}
        title={
          isOpen
            ? "Rejoindre le groupe"
            : "Il n'est pas possible de rejoindre ce groupe"
        }
        onClick={onJoin}
        icon="plus"
      >
        Rejoindre
      </Button>
      {isOpen && (
        <Button
          type="button"
          loading={isLoading}
          disabled={isLoading}
          onClick={onFollow}
          icon="rss"
        >
          Suivre
        </Button>
      )}
    </StyledWrapper>
  );
};
NonMemberActions.propTypes = {
  onJoin: PropTypes.func,
  onFollow: PropTypes.func,
  isLoading: PropTypes.bool,
  isOpen: PropTypes.bool,
};
export default NonMemberActions;
