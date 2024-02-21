import PropTypes from "prop-types";
import React, { useCallback } from "react";
import Select, { components } from "react-select";
import styled, { keyframes } from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

import { useResponsiveMemo } from "@agir/front/genericComponents/grid";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";

const slideIn = keyframes`
  from {
    opacity: 0;
    transform: translateY(100%);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
`;

const StyledLabel = styled.span``;
const StyledHelpText = styled.span``;
const StyledError = styled.span``;
const StyledMenuList = styled.div``;

const BackgroundOpacity = styled.div`
  @media (max-width: ${style.collapse}px) {
    z-index: -1;
    height: 100vh;
    width: 100vw;
    position: fixed;
    top: 0;
    left: 0;
    background-color: black;
  }
`;

const CustomMenu = (props) => (
  <components.Menu {...props}>
    {props.children}
    <BackgroundOpacity />
  </components.Menu>
);

const StyledField = styled.label`
  display: flex;
  flex-flow: column nowrap;
  gap: 0.5rem;
  font-size: 1rem;
  font-weight: 400;
  line-height: 1;
  margin-bottom: 0;

  ${StyledLabel} {
    font-weight: 600;
  }

  ${StyledHelpText} {
    line-height: 1.5;

    small {
      font-size: 0.875rem;
    }
  }

  .select__indicator-separator {
    display: none;
  }
  .select__dropdown-indicator {
    color: ${({ $invalid }) => ($invalid ? style.redNSP : style.black100)};
  }

  .select__control {
    border-radius: ${style.softBorderRadius};
    border: 1px solid;
    max-width: 100%;
    min-height: 2.5rem;
    line-height: 1.5;
    font-size: ${({ $small }) => ($small ? "0.875rem" : "1rem")};
    font-weight: ${({ $small }) => ($small ? "600" : "auto")};

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
        $invalid ? style.redNSP : style.black500};
    }

    &.select__control--is-disabled {
      background-color: ${style.black100};
    }

    & .select__placeholder {
      white-space: nowrap;
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

  .select__menu {
    border: 1px solid ${style.black100};
    box-shadow: 0px 3px 2px rgba(0, 35, 44, 0.05);
    margin-top: 0;
    border-radius: 0;
    padding: 0;

    @media (max-width: ${style.collapse}px) {
      position: fixed;
      bottom: 0;
      top: unset;
      left: 0;
      right: 0;
      width: 100%;
      margin: 0;
      max-height: 40vh;
      border-radius: ${style.borderRadius} ${style.borderRadius} 0 0;
      overflow-x: hidden;
      overflow-y: auto;
      animation: ${slideIn} 200ms ease-out;
    }
  }

  ${BackgroundOpacity} {
    @media (max-width: ${style.collapse}px) {
      display: block;
      opacity: ${(props) => (props.$searchable ? 0.15 : 0.5)};
    }
  }

  .select__menu-list {
    @media (max-width: ${style.collapse}px) {
      padding-bottom: 60px;
      max-height: 100%;
    }

    @media (max-width: ${style.collapse}px) {
      padding-top: 10px;
      background-color: white;
    }

    footer {
      position: absolute;
      bottom: 0;
      width: 100%;
      display: none;

      @media (max-width: ${style.collapse}px) {
        display: block;
        z-index: 1;
        box-shadow: -10px -10px 15px white;
      }

      &::before {
        content: "";
        display: block;
        width: 80%;
        height: 1px;
        margin: 0 auto;
        background-color: ${style.black200};
      }

      button {
        display: flex;
        align-items: center;
        justify-content: center;
        background-color: white;
        box-shadow: none;
        border: none;
        height: 54px;
        font-size: inherit;
        width: 100%;
        cursor: pointer;
      }
    }
  }

  .select__option {
    padding: 10px 1rem;
    display: flex;
    align-items: center;
    line-height: 1.2;
    cursor: pointer;

    ${(props) =>
      props.$noWrapOptions
        ? `
        display: block;
        max-width: 100%;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    `
        : ""}
  }

  ${StyledError} {
    line-height: 1.3;
    display: ${({ $invalid }) => ($invalid ? "flex" : "none")};
    color: ${style.redNSP};
  }
`;

const Control = ({ children, ...props }) => (
  <components.Control {...props}>
    {!!props.selectProps.searchIcon && (
      <RawFeatherIcon name="search" width="1rem" height="1rem" />
    )}
    {children}
  </components.Control>
);
Control.propTypes = {
  children: PropTypes.node,
  selectProps: PropTypes.shape({
    searchIcon: PropTypes.bool,
  }),
};

const SelectMenuList = (props) => {
  const {
    setValue,
    selectProps: { value },
  } = props;

  const handleClick = useCallback(() => {
    setValue(value || null);
  }, [setValue, value]);

  return (
    <StyledMenuList>
      <components.MenuList {...props} />
      <footer>
        <button type="button" onClick={handleClick}>
          Fermer
        </button>
      </footer>
    </StyledMenuList>
  );
};
SelectMenuList.propTypes = {
  setValue: PropTypes.func,
  selectProps: PropTypes.shape({
    value: PropTypes.any,
  }),
};

const selectFieldTheme = (theme) => ({
  ...theme,
  colors: {
    ...theme.colors,
    primary: style.primary500,
    primary25: style.black100,
  },
});

const SelectField = (props) => {
  const {
    id,
    onChange,
    value = "",
    error,
    label,
    helpText,
    options,
    isSearchable,
    small,
    noWrapOptions,
    searchIcon = false,
    className = "",
    ...rest
  } = props;

  const maxMenuHeight = useResponsiveMemo(isSearchable ? 124 : 238, 238);

  return (
    <StyledField
      htmlFor={id}
      $valid={!error}
      $invalid={!!error}
      $empty={!!value}
      $searchable={!!isSearchable}
      $small={small}
      $noWrapOptions={noWrapOptions}
    >
      {label && <StyledLabel>{label}</StyledLabel>}
      {helpText && <StyledHelpText>{helpText}</StyledHelpText>}
      <Select
        {...rest}
        className={`${className} select-container`.trim()}
        searchIcon={searchIcon}
        noOptionsMessage={() => "Aucune option disponible"}
        maxMenuHeight={maxMenuHeight}
        classNamePrefix="select"
        isDisabled={!!rest.disabled}
        isSearchable={!!isSearchable}
        inputId={id}
        options={options}
        onChange={onChange}
        value={value}
        theme={selectFieldTheme}
        captureMenuScroll={false}
        menuShouldScrollIntoView={false}
        components={{
          Menu: CustomMenu,
          Control,
        }}
      />
      <StyledError>{error}</StyledError>
    </StyledField>
  );
};

SelectField.propTypes = {
  value: PropTypes.any,
  onChange: PropTypes.func,
  options: PropTypes.arrayOf(PropTypes.object),
  id: PropTypes.string,
  label: PropTypes.node,
  helpText: PropTypes.node,
  error: PropTypes.node,
  isSearchable: PropTypes.bool,
  small: PropTypes.bool,
  noWrapOptions: PropTypes.bool,
  searchIcon: PropTypes.bool,
  className: PropTypes.string,
};

export default SelectField;
