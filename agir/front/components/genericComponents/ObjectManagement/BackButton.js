import React from "react";

import styled from "styled-components";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";

const StyledBackButton = styled.button`
  &,
  &:hover,
  &:focus {
    background-color: transparent;
    border: none;
    box-shadow: none;
    padding: 0 0 0.5rem;
    margin: 0;
    text-align: left;
    cursor: pointer;
  }
  &:hover,
  &:focus {
    opacity: 0.75;
  }
`;

const BackButton = ({ onBack }) => {
  return (
    <StyledBackButton type="button" onClick={onBack}>
      <RawFeatherIcon
        name="arrow-left"
        aria-label="Retour"
        width="1.5rem"
        height="1.5rem"
      />
    </StyledBackButton>
  );
};

export default BackButton;
