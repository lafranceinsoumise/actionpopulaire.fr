import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";

const Button = styled.button`
  display: block;
  border: none;
  background-color: ${(props) => props.theme.background0};
  padding: 0.75rem 1rem;
  font-size: 1rem;
  font-weight: 500;
  display: flex;
  flex-direction: row;
  align-items: center;
  text-align: left;
  color: ${(props) => props.theme.primary500};
  cursor: pointer;

  ${RawFeatherIcon} {
    padding: 0.25rem;
    background-color: ${(props) => props.theme.primary100};
    color: ${(props) => props.theme.primary500};
    border-radius: 40px;
    margin-right: 1rem;

    svg {
      width: 1.5rem;
      height: 1.5rem;

      @media (max-width: ${(props) => props.theme.collapse}px) {
        width: 1rem;
        height: 1rem;
      }
    }
  }
`;

const ButtonAddList = ({ label, onClick }) => {
  return (
    <Button onClick={onClick}>
      <RawFeatherIcon name="plus" />
      <span>{label}</span>
    </Button>
  );
};

ButtonAddList.propTypes = {
  label: PropTypes.string.isRequired,
  onClick: PropTypes.func.isRequired,
};
export default ButtonAddList;
