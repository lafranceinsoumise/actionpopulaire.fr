import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";

const StyledButton = styled.button`
  width: 100%;
  display: block;
  background-color: ${style.white};
  padding: 0.75rem 1rem;
  font-size: 1rem;
  font-weight: 500;
  display: flex;
  flex-direction: row;
  align-items: center;
  text-align: left;
  color: ${style.primary500};
  cursor: pointer;

  &:hover,
  &:focus,
  &:active  {
    text-decoration: none;
    color: ${style.primary500};
  }

  &:focus {
    outline: 1px dotted ${style.black500};
  }

  ${RawFeatherIcon} {
    padding: 0.25rem;
    background-color: ${(props) =>
      props.icon === "plus" ? style.primary100 : "transparent"};
    color: ${style.primary500};
    border-radius: 40px;
    margin-right: 1rem;

    svg {
      width: 1.5rem;
      height: 1.5rem;

      @media (max-width: ${style.collapse}px) {
        width: 1rem;
        height: 1rem;
      }
    }
  }
`;

const ListButton = ({ label, ...buttonProps }) => (
  <StyledButton {...buttonProps}>
    {buttonProps.icon && <RawFeatherIcon name={buttonProps.icon} />}
    <span>{label}</span>
  </StyledButton>
);
ListButton.propTypes = {
  label: PropTypes.string.isRequired,
  icon: PropTypes.string,
};

export const ButtonAddList = (props) => <ListButton {...props} icon="plus" />;

ButtonAddList.propTypes = {
  label: PropTypes.string.isRequired,
  onClick: PropTypes.func.isRequired,
};

export default ListButton;
