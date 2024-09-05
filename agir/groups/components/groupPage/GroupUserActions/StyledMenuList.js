import styled from "styled-components";

import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";

const StyledList = styled.ul`
  width: 100%;
  cursor: pointer;
  display: flex;
  flex-flow: column nowrap;
  align-items: stretch;
  list-style: none;
  color: ${(props) => props.theme.primary500};
  padding: 0;
  margin: 0;
  gap: 0.5rem;

  @media (max-width: ${(props) => props.theme.collapse}px) {
    margin: 0;
    padding: 1.5rem;
  }

  li {
    margin: 0;
  }

  button {
    display: flex;
    flex-flow: row nowrap;
    align-items: start;
    justify-content: start;
    gap: 0.5rem;
    text-align: left;
    border: none;
    padding: 0;
    margin: 0;
    cursor: pointer;
    font-size: 0.875rem;
    font-weight: 400;
    color: ${(props) => props.theme.text1000};

    &,
    &:hover,
    &:focus {
      background-color: transparent;
      border: 0;
      outline: 0;
    }

    &[disabled],
    &[disabled]:hover,
    &[disabled]:focus {
      opacity: 0.75;
      cursor: default;
    }

    ${RawFeatherIcon} {
      color: ${(props) => props.theme.primary500};
      height: 1.25rem;
    }
  }
`;

export default StyledList;
