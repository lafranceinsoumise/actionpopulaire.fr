import Async from "react-select/async";
import { components } from "react-select";
import PropTypes from "prop-types";
import React, { useCallback } from "react";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

import Button from "@agir/front/genericComponents/Button";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";

const StyledLabel = styled.span``;
const StyledHelpText = styled.span``;
const StyledError = styled.span``;

const StyledSelectContainer = styled(components.SelectContainer)``;
const StyledControl = styled(components.Control)``;
const StyledMenu = styled(components.Menu)``;
const StyledNoOptionsMessage = styled(components.NoOptionsMessage)``;
const StyledLoadingMessage = styled(components.LoadingMessage)``;
const StyledOption = styled(components.Option)`
  && {
    display: flex;
    flex-flow: row nowrap;
    align-items: center;
    font-size: 1rem;
    padding: 0.5rem 1rem;
    color: ${({ isSelected }) =>
      isSelected ? style.primary500 : style.black1000};
    cursor: ${({ isSelected, isDisabled }) =>
      isSelected || isDisabled ? "default" : "pointer"};
    background-color: ${({ isFocused, isSelected }) => {
      if (isFocused && !isSelected) {
        return style.black50;
      }
      return "transparent";
    }};

    ${RawFeatherIcon} {
      color: ${style.white};
      background-color: ${style.primary500};
      height: 2rem;
      width: 2rem;
      display: flex;
      align-items: center;
      justify-content: center;
      border-radius: 100%;
      margin-right: 1rem;
    }

    p {
      margin: 0;
      padding: 0;

      strong,
      span {
        display: block;
        line-height: 1.5;
        font-size: 1rem;
      }

      strong {
        font-weight: 500;
      }

      span {
        font-size: 1rem;
        font-weight: 400;
        color: ${({ isSelected }) =>
          isSelected ? style.primary500 : style.black700};
      }
    }

    ${Button} {
      display: ${({ isSelected }) => (isSelected ? "none" : "inline")};
      margin-left: auto;
      font-size: 1rem;
      font-weight: 700;
      height: 2rem;
    }
  }
`;

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
  }

  ${StyledSelectContainer} {
    grid-row: 3;
    grid-column: 1/3;

    .select__indicator-separator {
      display: none;
    }
    .select__dropdown-indicator {
      color: ${({ $invalid }) => ($invalid ? style.redNSP : style.black100)};
    }
  }

  ${StyledControl} {
    border-radius: ${style.softBorderRadius};
    border: 1px solid;
    max-width: 100%;
    height: 40px;
    font-size: 1rem;
    line-height: 1.5rem;

    &,
    &:hover,
    &:focus,
    &.select__control--is-focused {
      outline: none;
      box-shadow: none;
      border-color: ${({ $invalid }) =>
        $invalid ? style.redNSP : style.black100};
    }

    &:focus,
    &.select__control--is-focused {
      border-color: ${({ $invalid }) =>
        $invalid ? style.redNSP : style.black1000};
    }

    ${RawFeatherIcon} {
      color: ${style.black700};
      width: 1.5rem;
      height: 100%;
      display: flex;
      align-items: center;
      justify-content: flex-end;
      margin: 0;
    }
  }

  ${StyledMenu} {
    border: 1px solid ${style.black100};
    box-shadow: 0px 4px 4px rgba(0, 0, 0, 0.25);
    margin-top: -1px;
    border-radius: 0;
    padding: 0;
  }

  ${StyledNoOptionsMessage},
  ${StyledLoadingMessage} {
    text-align: left;
  }

  ${StyledError} {
    display: ${({ $invalid }) => ($invalid ? "flex" : "none")};
    grid-row: 4;
    grid-column: 1/3;
    color: ${style.redNSP};
  }
`;

const Control = ({ children, ...props }) => (
  <StyledControl {...props}>
    <RawFeatherIcon name="search" width="1rem" height="1rem" />
    {children}
  </StyledControl>
);
Control.propTypes = {
  children: PropTypes.node,
};

const Option = ({ innerRef, ...innerProps }) => {
  const { data } = innerProps;
  const label = (data && data.label) || innerProps.label;
  const sublabel = (data && data.sublabel) || null;
  const icon = data.icon || null;
  const buttonLabel = data.buttonLabel || null;
  return (
    <StyledOption ref={innerRef} {...innerProps}>
      {icon && <RawFeatherIcon name={icon} widht="1rem" height="1rem" />}
      <p>
        <strong>Choisir: {label}</strong>
        {sublabel ? <span>{sublabel}</span> : null}
      </p>
      {buttonLabel && (
        <Button type="button" color="choose" small>
          {buttonLabel}
        </Button>
      )}
    </StyledOption>
  );
};
Option.propTypes = {
  innerRef: PropTypes.any,
  data: PropTypes.shape({
    value: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
    label: PropTypes.string,
    sublabel: PropTypes.string,
    buttonLabel: PropTypes.string,
  }).isRequired,
};

const SearchAndSelectField = (props) => {
  const {
    id,
    defaultOptions,
    onChange,
    onSearch,
    isLoading,
    value,
    error,
    label,
    helpText,
    ...rest
  } = props;

  const loadingMessage = useCallback(() => "Recherche...", []);
  const noOptionsMessage = useCallback(
    ({ inputValue }) =>
      inputValue.length < 3
        ? "Entrez au moins 3 lettres pour chercher"
        : "Pas de résultats",
    []
  );

  return (
    <StyledField
      htmlFor={id}
      $valid={!error}
      $invalid={!!error}
      $empty={!!value}
    >
      {label && <StyledLabel>{label}</StyledLabel>}
      {helpText && <StyledHelpText>{helpText}</StyledHelpText>}
      <Async
        {...rest}
        value={value}
        isLoading={isLoading}
        loadOptions={onSearch}
        loadingMessage={loadingMessage}
        noOptionsMessage={noOptionsMessage}
        onChange={onChange}
        defaultOptions={defaultOptions}
        classNamePrefix="select-search"
        isDisabled={!!rest.disabled}
        inputId={id}
        components={{
          Option,
          Control,
          Menu: StyledMenu,
          Container: StyledSelectContainer,
          IndicatorSeparator: null,
          LoadingMessage: StyledLoadingMessage,
          NoOptionsMessage: StyledNoOptionsMessage,
        }}
      />
      <StyledError>{error}</StyledError>
    </StyledField>
  );
};

SearchAndSelectField.propTypes = {
  value: PropTypes.any,
  onChange: PropTypes.func.isRequired,
  onSearch: PropTypes.func.isRequired,
  defaultOptions: PropTypes.oneOfType([PropTypes.array, PropTypes.bool]),
  id: PropTypes.string,
  label: PropTypes.string,
  helpText: PropTypes.string,
  error: PropTypes.string,
  isLoading: PropTypes.bool,
};

export default SearchAndSelectField;
