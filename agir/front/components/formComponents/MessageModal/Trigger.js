import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import * as style from "@agir/front/genericComponents/_variables.scss";

import Button from "@agir/front/genericComponents/Button";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";

const StyledFloatingButton = styled(Button)`
  margin: 0 auto;
  height: 54px;
  padding: 0 2rem;
  position: fixed;
  bottom: 2rem;
  left: 50%;
  transform: translateX(-50%);
  z-index: 20;

  span {
    text-overflow: ellipsis;
    white-space: nowrap;
    overflow: hidden;
  }

  ${RawFeatherIcon} {
    margin-right: 12px;
    position: relative;
    display: inline-flex;
    align-items: center;
    justify-content: center;

    &::before {
      content: "+";
      position: absolute;
      color: white;
      font-size: 11px;
      font-weight: 600;
      top: 2px;
      left: 1px;
      line-height: 0;
    }
    svg {
      margin-left: 3px;
    }
  }
`;

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
    width: 2rem;
    height: 2rem;
    background-color: ${style.primary500};
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

export const FloatingTrigger = (props) => {
  const { label, onClick } = props;

  return (
    <StyledFloatingButton color="primary" onClick={onClick}>
      <RawFeatherIcon
        name="edit-2"
        color="white"
        width="1rem"
        height="1rem"
        strokeWidth={3}
      />
      <span>{label || "Nouveau message"}</span>
    </StyledFloatingButton>
  );
};

const Trigger = (props) => {
  const { label, onClick, outlined } = props;

  return (
    <StyledButton onClick={onClick} $outlined={outlined}>
      <RawFeatherIcon
        name="edit-2"
        color="white"
        width="13px"
        height="13px"
        strokeWidth={3}
      />
      <span>{label || "Envoyer un message au groupe"}</span>
    </StyledButton>
  );
};
FloatingTrigger.propTypes = Trigger.propTypes = {
  label: PropTypes.string,
  onClick: PropTypes.func.isRequired,
  outlined: PropTypes.bool,
};
export default Trigger;
