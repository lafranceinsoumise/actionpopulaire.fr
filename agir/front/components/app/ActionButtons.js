import React from "react";
import styled from "styled-components";

import Link from "./Link";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";

const StyledButton = styled(Link)`
  width: 5.063rem;
  display: flex;
  flex-flow: column nowrap;
  align-items: center;
  text-align: center;
  color: ${(props) => props.theme.black1000};

  @media (min-width: ${(props) => props.theme.collapse}px) {
    flex-flow: row nowrap;
    width: 100%;
    text-align: left;
  }

  &:hover,
  &:focus {
    color: ${(props) => props.theme.black1000};
    text-decoration: none;
    outline: none;

    @media (min-width: ${(props) => props.theme.collapse}px) {
      opacity: 0.9;
    }
  }

  & > span {
    width: 3.125rem;
    height: 3.125rem;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    background-color: ${(props) => props.theme[props.color]};
    color: ${(props) => props.theme.white};
    border-radius: 100%;

    @media (min-width: ${(props) => props.theme.collapse}px) {
      transform: scale(0.75);
      transform-origin: center left;
    }

    & > * {
      flex: 0 0 auto;
    }
  }

  & > strong {
    font-weight: 400;
    font-size: 0.875rem;

    @media (max-width: ${(props) => props.theme.collapse}px) {
      margin-top: 0.688rem;
    }
  }

  &:hover > strong,
  &:focus > strong {
    @media (min-width: ${(props) => props.theme.collapse}px) {
      color: ${(props) => props.theme.primary500};
    }
  }
`;

const StyledButtons = styled.nav`
  padding: 0;
  margin: 0;

  @media (max-width: ${(props) => props.theme.collapse}px) {
    display: flex;
    justify-content: center;
    gap: 2rem;
  }

  ${StyledButton} {
    flex: 0 0 auto;
  }
`;

const ActionButtons = () => {
  return (
    <StyledButtons>
      <StyledButton route="createEvent" color="secondary500">
        <span>
          <svg
            width="24"
            height="24"
            viewBox="0 0 16 16"
            fill="none"
            stroke="#000A2C"
            strokeWidth="1.33"
            strokeLinecap="round"
            strokeLinejoin="round"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path d="M14 8.99999V3.99999C14 3.26361 13.403 2.66666 12.6667 2.66666H3.33333C2.59695 2.66666 2 3.26361 2 3.99999V13.3333C2 14.0697 2.59695 14.6667 3.33333 14.6667H8.66667" />
            <path d="M10.6667 1.33334V4.00001" />
            <path d="M5.33331 1.33334V4.00001" />
            <path d="M2 6.66666H14" />
            <path d="M12.6667 11.3333V15.3333" />
            <path d="M14.6667 13.3333H10.6667" />
          </svg>
        </span>
        <strong>Créer un événement</strong>
      </StyledButton>
      <StyledButton route="createContact" color="primary500">
        <RawFeatherIcon name="user-plus" />
        <strong>Ajouter un contact</strong>
      </StyledButton>
      <StyledButton route="donations" color="redNSP">
        <RawFeatherIcon name="heart" />
        <strong>Faire un don</strong>
      </StyledButton>
    </StyledButtons>
  );
};

export default ActionButtons;
