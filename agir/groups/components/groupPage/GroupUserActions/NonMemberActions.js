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
  const { onJoin, onFollow, isLoading } = props;

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
    </StyledWrapper>
  );
};
NonMemberActions.propTypes = {
  onJoin: PropTypes.func,
  onFollow: PropTypes.func,
  isLoading: PropTypes.bool,
};
export default NonMemberActions;
