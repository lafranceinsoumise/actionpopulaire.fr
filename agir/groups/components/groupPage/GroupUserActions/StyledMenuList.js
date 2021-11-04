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

  @media (max-width: ${(props) => props.theme.collapse}px) {
    margin: 0;
    padding: 1.5rem;
  }

  li + li {
    margin-top: 0.5rem;
  }

  button {
    display: flex;
    align-items: center;
    border: none;
    padding: 0;
    margin: 0;
    cursor: pointer;
    font-size: 0.875rem;
    font-weight: 400;
    color: ${(props) => props.theme.black1000};
    height: 1.25rem;

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
    }
  }
`;

export default StyledList;
