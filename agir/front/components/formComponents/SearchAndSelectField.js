import Async from "react-select/async";
import { components } from "react-select";
import PropTypes from "prop-types";
import React, { useCallback, useMemo, useState } from "react";
import styled from "styled-components";

import { debounce } from "@agir/lib/utils/promises";

import Button from "@agir/front/genericComponents/Button";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";
import FaIcon from "../genericComponents/FaIcon";

const StyledFaIcon = styled(FaIcon).attrs((props) => ({
  $color: props.$color || props.theme.primary500,
}))`
  color: ${({ $color }) =>
    (parseInt($color.substring(1, 3), 16) * 299 +
      parseInt($color.substring(3, 5), 16) * 587 +
      parseInt($color.substring(5, 7), 16) * 114) /
      1000 >=
    128
      ? "#000000EE"
      : "#FFFFFFDD"};
  background-color: ${(props) => props.$color};
`;
const StyledLabel = styled.span``;
const StyledHelpText = styled.span``;
const StyledError = styled.span``;

const StyledNoOptionsMessage = styled(components.NoOptionsMessage)``;
const StyledLoadingMessage = styled(components.LoadingMessage)``;

export const useRemoteSearch = (fetcher, formatter) => {
  const [options, setOptions] = useState();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSearch = useMemo(
    () =>
      debounce(async (searchTerm) => {
        setIsLoading(true);
        setOptions(undefined);
        setError(null);
        const { data, error } = await fetcher(searchTerm);
        setIsLoading(false);
        setError(error);
        const options =
          data && typeof formatter === "function" ? formatter(data) : data;
        setOptions(options);
        return options;
      }, 600),
    [fetcher, formatter],
  );

  return [handleSearch, options, isLoading, error];
};

const StyledField = styled.label`
  width: 100%;
  display: flex;
  flex-flow: column nowrap;
  gap: 4px;
  margin-bottom: 0;
  align-items: stretch;
  font-size: 1rem;
  font-weight: 400;
  line-height: 1.5;

  ${StyledLabel} {
    font-weight: 600;
  }

  .select-search-container {
    .select-search__indicator-separator {
      display: none;
    }
    .select-search__dropdown-indicator {
      color: ${({ $invalid }) =>
        $invalid
          ? (props) => props.theme.redNSP
          : (props) => props.theme.black100};
    }
  }

  .select-search__control {
    border-radius: ${(props) => props.theme.softBorderRadius};
    border: 1px solid;
    max-width: 100%;
    height: 40px;
    font-size: 1rem;

    &,
    &:hover,
    &:focus,
    &.select-search__control--is-focused {
      outline: none;
      box-shadow: none;
      border-color: ${({ $invalid }) =>
        $invalid
          ? (props) => props.theme.redNSP
          : (props) => props.theme.black100};
    }

    &:focus,
    &.select-search__control--is-focused {
      border-color: ${({ $invalid }) =>
        $invalid
          ? (props) => props.theme.redNSP
          : (props) => props.theme.black500};
    }

    .select-search__placeholder {
      white-space: nowrap;
      max-width: 100%;
      text-overflow: ellipsis;
      overflow: hidden;
    }

    ${RawFeatherIcon} {
      color: ${(props) => props.theme.black700};
      width: 1.5rem;
      height: 100%;
      display: flex;
      align-items: center;
      justify-content: flex-end;
      margin: 0;
    }
  }

  .select-search__menu {
    border: 1px solid ${(props) => props.theme.black100};
    box-shadow: 0px 4px 4px rgba(0, 0, 0, 0.25);
    margin-top: -1px;
    border-radius: 0;
    padding: 0;
  }

  .select-search__option {
    display: flex;
    flex-flow: row nowrap;
    align-items: center;
    font-size: 1rem;
    padding: 0.5rem 1rem;
    color: ${(props) => props.theme.black1000};
    cursor: pointer;
    background-color: transparent;

    &.select-search__option--is-focused {
      background-color: ${(props) => props.theme.black50};
    }

    &.select-search__option--is-selected {
      cursor: default;
    }

    &.select-search__option--is-selected {
      color: ${(props) => props.theme.primary500};
      background-color: transparent;
    }

    ${StyledFaIcon} {
      flex: 0 0 auto;
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
          isSelected
            ? (props) => props.theme.primary500
            : (props) => props.theme.black700};
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

  ${StyledNoOptionsMessage},
  ${StyledLoadingMessage} {
    text-align: left;
  }

  ${StyledError} {
    display: ${({ $invalid }) => ($invalid ? "flex" : "none")};
    color: ${(props) => props.theme.redNSP};
  }
`;

const Control = ({ children, ...props }) => (
  <components.Control {...props}>
    <RawFeatherIcon name="search" width="1rem" height="1rem" />
    {children}
  </components.Control>
);
Control.propTypes = {
  children: PropTypes.node,
};

const Option = (props) => {
  const { data } = props;
  const label = (data && data.label) || props.label;
  const sublabel = (data && data.sublabel) || null;
  const buttonLabel = data.buttonLabel || null;

  return (
    <components.Option {...props}>
      {data?.icon && (
        <StyledFaIcon $color={data?.iconColor} icon={data.icon} size="1rem" />
      )}
      <p>
        <strong>{label}</strong>
        {sublabel ? <span>{sublabel}</span> : null}
      </p>
      {buttonLabel && (
        <Button type="button" color="choose" small>
          {buttonLabel}
        </Button>
      )}
    </components.Option>
  );
};
Option.propTypes = {
  innerRef: PropTypes.any,
  data: PropTypes.shape({
    value: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
    label: PropTypes.string,
    sublabel: PropTypes.string,
    buttonLabel: PropTypes.string,
    icon: PropTypes.string,
    iconColor: PropTypes.string,
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
    minSearchTermLength = 3,
    ...rest
  } = props;

  const loadingMessage = useCallback(() => "Recherche...", []);
  const noOptionsMessage = useCallback(
    ({ inputValue }) =>
      inputValue.length < minSearchTermLength
        ? `Entrez au moins ${minSearchTermLength} lettre${
            minSearchTermLength > 1 ? "s" : ""
          } pour chercher`
        : "Pas de résultats",
    [minSearchTermLength],
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
        }}
      />
      <StyledError>{error}</StyledError>
    </StyledField>
  );
};

SearchAndSelectField.propTypes = {
  value: PropTypes.any,
  onChange: PropTypes.func,
  onSearch: PropTypes.func.isRequired,
  defaultOptions: PropTypes.oneOfType([PropTypes.array, PropTypes.bool]),
  id: PropTypes.string,
  label: PropTypes.string,
  helpText: PropTypes.string,
  error: PropTypes.string,
  isLoading: PropTypes.bool,
  minSearchTermLength: PropTypes.number,
};

export default SearchAndSelectField;
