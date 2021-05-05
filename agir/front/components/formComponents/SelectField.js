import PropTypes from "prop-types";
import React, { useCallback } from "react";
import Select, { components } from "react-select";
import styled, { keyframes } from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

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

const StyledSelectContainer = styled(components.SelectContainer)``;
const StyledControl = styled(components.Control)``;
const StyledMenu = styled(components.Menu)``;
const StyledMenuList = styled.div``;
const StyledOption = styled(components.Option)``;
const StyledError = styled.span``;

const StyledField = styled.label`
  display: grid;
  grid-template-columns: 1fr auto;
  grid-template-rows: auto auto auto auto;
  grid-gap: 4px 0.75rem;
  align-items: stretch;
  font-size: 1rem;
  font-weight: 400;
  line-height: 1;
  margin-bottom: 0;

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
    border-radius: 0;
    border: 1px solid;
    max-width: 100%;
    height: 40px;
    font-size: 1rem;

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

    @media (max-width: ${style.collapse}px) {
      font-size: 1rem;
    }
  }

  ${StyledMenu} {
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
      border-radius: 0.5rem 0.5rem 0 0;
      padding-top: 0.875rem;
      max-height: 388px;
      overflow-x: hidden;
      overflow-y: auto;
      animation: ${slideIn} 200ms ease-out;
    }
  }

  ${StyledMenuList} {
    @media (max-width: ${style.collapse}px) {
      padding-bottom: 60px;
      max-height: 100%;
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

  ${StyledOption} {
    padding: 10px 1rem;
    display: flex;
    align-items: center;
    line-height: 1.125;
    cursor: pointer;
  }

  ${StyledError} {
    display: ${({ $invalid }) => ($invalid ? "flex" : "none")};
    grid-row: 4;
    grid-column: 1/3;
    color: ${style.redNSP};
  }
`;

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
        <button onClick={handleClick}>Fermer</button>
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
    ...rest
  } = props;

  return (
    <StyledField
      htmlFor={id}
      $valid={!error}
      $invalid={!!error}
      $empty={!!value}
    >
      {label && <StyledLabel>{label}</StyledLabel>}
      {helpText && <StyledHelpText>{helpText}</StyledHelpText>}
      <Select
        {...rest}
        classNamePrefix="select"
        isDisabled={!!rest.disabled}
        isSearchable={!!rest.isSearchable}
        inputId={id}
        options={options}
        onChange={onChange}
        value={value}
        theme={selectFieldTheme}
        captureMenuScroll={false}
        components={{
          Control: StyledControl,
          SelectContainer: StyledSelectContainer,
          Menu: StyledMenu,
          MenuList: SelectMenuList,
          Option: StyledOption,
        }}
      />
      <StyledError>{error}</StyledError>
    </StyledField>
  );
};

SelectField.propTypes = {
  value: PropTypes.any,
  onChange: PropTypes.func.isRequired,
  options: PropTypes.arrayOf(PropTypes.object),
  id: PropTypes.string,
  label: PropTypes.string,
  helpText: PropTypes.string,
  error: PropTypes.string,
};

export default SelectField;
