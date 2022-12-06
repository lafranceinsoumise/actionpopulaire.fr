import Cleave from "cleave.js/react";
import PropTypes from "prop-types";
import React, { forwardRef } from "react";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

import FeatherIcon from "@agir/front/genericComponents/FeatherIcon";

import "cleave.js/dist/addons/cleave-phone.fr";

const StyledLabel = styled.span``;
const StyledHelpText = styled.span``;
const StyledInput = styled.span``;
const StyledIcon = styled.span``;
const StyledError = styled.span``;

const StyledField = styled.label`
  display: grid;
  grid-template-columns: 1fr auto;
  grid-template-rows: auto auto auto auto;
  grid-gap: 4px 0.75rem;
  margin-bottom: 0;
  align-items: stretch;
  font-size: 1rem;
  font-weight: 400;
  line-height: 1;

  ${StyledLabel} {
    grid-row: 1;
    grid-column: 1/3;
    font-weight: 600;
  }
  ${StyledHelpText} {
    grid-row: 2;
    grid-column: 1/3;
    line-height: 1.5;
  }

  ${StyledInput} {
    grid-row: 3;
    grid-column: 1/3;

    input {
      display: block;
      border-radius: ${style.softBorderRadius};
      border: 1px solid;
      border-color: ${({ $invalid }) =>
        $invalid ? style.redNSP : style.black100};
      width: 100%;
      padding: 0.5rem;
      padding-right: ${({ $invalid }) => ($invalid ? "3.25rem" : "0.5rem")};
      height: 40px;
      font-size: 1rem;

      &:focus {
        border-color: ${({ $invalid }) =>
          $invalid ? style.redNSP : style.black500};
      }
    }
  }
  ${StyledIcon} {
    display: ${({ $invalid }) => ($invalid ? "flex" : "none")};
    grid-row: 3;
    grid-column: 2/3;
    align-items: flex-start;
    justify-content: flex-end;
    padding: 0.5rem;
    color: ${style.redNSP};
  }
  ${StyledError} {
    display: ${({ $invalid }) => ($invalid ? "flex" : "none")};
    grid-row: 4;
    grid-column: 1/3;
    color: ${style.redNSP};
  }
`;

const PhoneField = forwardRef((props, ref) => {
  const { id, onChange, value = "", error, label, helpText, ...rest } = props;

  return (
    <StyledField
      htmlFor={id}
      $valid={!error}
      $invalid={!!error}
      $empty={!!value}
    >
      {label && <StyledLabel>{label}</StyledLabel>}
      {helpText && <StyledHelpText>{helpText}</StyledHelpText>}
      <StyledInput>
        <Cleave
          {...rest}
          type="phone"
          htmlRef={ref}
          id={id}
          options={{ phone: true, phoneRegionCode: "FR" }}
          name="phone"
          value={value || ""}
          onChange={onChange}
          onInit={(owner) => {
            owner.lastInputValue = value || "";
          }}
        />
      </StyledInput>
      <StyledIcon>
        <FeatherIcon name="alert-circle" />
      </StyledIcon>
      <StyledError>{error}</StyledError>
    </StyledField>
  );
});

PhoneField.propTypes = {
  value: PropTypes.any,
  onChange: PropTypes.func.isRequired,
  id: PropTypes.string,
  label: PropTypes.node,
  helpText: PropTypes.node,
  error: PropTypes.string,
};

PhoneField.displayName = "PhoneField";

export default PhoneField;
