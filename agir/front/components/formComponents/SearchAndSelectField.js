import Async from "react-select/async";
import { components } from "react-select";
import PropTypes from "prop-types";
import React, { useCallback, useMemo, useState } from "react";
import styled from "styled-components";

import { debounce } from "@agir/lib/utils/promises";
import style from "@agir/front/genericComponents/_variables.scss";

import Button from "@agir/front/genericComponents/Button";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";

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
    [fetcher, formatter]
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
      color: ${({ $invalid }) => ($invalid ? style.redNSP : style.black100)};
    }
  }

  .select-search__control {
    border-radius: ${style.softBorderRadius};
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
        $invalid ? style.redNSP : style.black100};
    }

    &:focus,
    &.select-search__control--is-focused {
      border-color: ${({ $invalid }) =>
        $invalid ? style.redNSP : style.black500};
    }

    .select-search__placeholder {
      white-space: nowrap;
      max-width: 100%;
      text-overflow: ellipsis;
      overflow: hidden;
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

  .select-search__menu {
    border: 1px solid ${style.black100};
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
    color: ${style.black1000};
    cursor: pointer;
    background-color: transparent;

    &.select-search__option--is-focused {
      background-color: ${style.black50};
    }

    &.select-search__option--is-selected {
      cursor: default;
    }

    &.select-search__option--is-selected {
      color: ${style.primary500};
      background-color: transparent;
    }

    ${RawFeatherIcon} {
      flex: 0 0 auto;
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

  ${StyledNoOptionsMessage},
  ${StyledLoadingMessage} {
    text-align: left;
  }

  ${StyledError} {
    display: ${({ $invalid }) => ($invalid ? "flex" : "none")};
    color: ${style.redNSP};
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
  const icon = data.icon || null;
  const buttonLabel = data.buttonLabel || null;
  return (
    <components.Option {...props}>
      {icon && <RawFeatherIcon name={icon} widht="1rem" height="1rem" />}
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
    [minSearchTermLength]
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
  onChange: PropTypes.func.isRequired,
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
