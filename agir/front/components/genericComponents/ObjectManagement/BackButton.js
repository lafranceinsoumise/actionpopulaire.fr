import React from "react";

import styled from "styled-components";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";

const StyledBackButton = styled.button`
  &,
  &:hover,
  &:focus {
    color: currentcolor;
    background-color: transparent;
    border: none;
    box-shadow: none;
    padding: 0 0 0.5rem;
    margin: 0;
    text-align: left;
    cursor: pointer;
  }
`;

const BackButton = (props) => {
  return (
    <StyledBackButton {...props} type="button">
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
