import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

import { RawFeatherIcon as FeatherIcon } from "@agir/front/genericComponents/FeatherIcon";

const StyledLabel = styled.span``;
const StyledBox = styled.span``;

const StyledField = styled.label`
  position: relative;
  display: flex;
  flex-flow: row nowrap;
  align-items: flex-start;
  font-size: 1rem;
  line-height: 1.5;
  cursor: ${({ $disabled }) => ($disabled ? "default" : "pointer")};

  input {
    position: absolute;
    z-index: -1;
    opacity: 0;
  }

  ${StyledBox} {
    display: flex;
    justify-content: center;
    align-items: center;
    flex: 0 0 auto;
    margin-top: 0.25rem;
    margin-right: 0.5rem;
    width: 1rem;
    height: 1rem;
    border-style: solid;
    border-width: ${({ $checked }) => ($checked ? 0 : 1)}px;
    border-color: ${({ $disabled }) =>
      $disabled ? style.black200 : style.black1000};
    background-color: ${({ $checked, $disabled }) => {
      if ($checked && $disabled) {
        return style.primary150;
      }
      if ($checked) {
        return style.primary500;
      }
      if ($disabled) {
        return style.black100;
      }
      return style.white;
    }};
    transition: all 200ms ease-in;
  }

  input:focus + ${StyledBox} {
    box-shadow: ${({ $disabled }) =>
      !$disabled ? `0 0 0 4px ${style.primary100}` : "none"};
  }

  ${StyledLabel} {
    flex: 1 1 auto;
    font-weight: 400;
    color: ${({ $disabled }) => ($disabled ? style.black500 : style.black1000)};
  }
`;

const CheckboxField = (props) => {
  const { id, onChange, value = false, label, ...rest } = props;

  return (
    <StyledField htmlFor={id} $checked={!!value} $disabled={rest.disabled}>
      <input
        {...rest}
        type="checkbox"
        id={id}
        onChange={onChange}
        checked={!!value}
      />
      <StyledBox>
        {!!value && (
          <FeatherIcon
            name="check"
            color="white"
            strokeWidth={4}
            width="12px"
            height="12px"
          />
        )}
      </StyledBox>
      {label && <StyledLabel>{label}</StyledLabel>}
    </StyledField>
  );
};

CheckboxField.propTypes = {
  value: PropTypes.bool,
  onChange: PropTypes.func.isRequired,
  id: PropTypes.string,
  label: PropTypes.node,
  disabled: PropTypes.bool,
};

export default CheckboxField;
