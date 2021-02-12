import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";

const StyledButton = styled.button`
  border: ${({ $outlined }) =>
    $outlined ? `1px solid ${style.primary500}` : "none"};
  margin: 0;
  text-decoration: none;
  background-color: ${style.white};
  cursor: pointer;
  text-align: center;
  -webkit-appearance: none;
  -moz-appearance: none;
  color: ${style.primary500};
  border-radius: 3px;
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
  height: 54px;
  padding: 0.5rem;

  @media (max-width: ${style.collapse}px) {
    border: ${({ $outlined }) =>
      $outlined ? `1px solid ${style.black100}` : "none"};
  }

  &:focus,
  &:hover {
    border: none;
    outline: none;
    opacity: 0.8;
  }

  span {
    font-size: 0.875rem;
    font-weight: 500;
    text-overflow: ellipsis;
    white-space: nowrap;
    overflow: hidden;
  }

  ${RawFeatherIcon} {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    background-color: ${style.primary500};
    width: 2rem;
    height: 2rem;
    margin-right: 12px;
    position: relative;
    border-radius: 100%;

    &::before {
      content: "+";
      position: absolute;
      color: white;
      font-size: 11px;
      font-weight: 600;
      top: 11px;
      left: 8px;
      line-height: 0;
    }
    svg {
      margin-left: 3px;
    }
  }
`;

const Trigger = (props) => {
  const { onClick, outlined } = props;

  return (
    <StyledButton onClick={onClick} $outlined={outlined}>
      <RawFeatherIcon
        name="edit-2"
        color="white"
        width="13px"
        height="13px"
        strokeWidth={3}
      />
      <span>Envoyer un message au groupe</span>
    </StyledButton>
  );
};
Trigger.propTypes = {
  onClick: PropTypes.func.isRequired,
  outlined: PropTypes.bool,
};
export default Trigger;
