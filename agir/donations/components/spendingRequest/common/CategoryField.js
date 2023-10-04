import Card from "@agir/front/genericComponents/Card";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";
import PropTypes from "prop-types";
import React, { useCallback, useMemo } from "react";
import styled from "styled-components";

import { CATEGORY_OPTIONS, FALLBACK_CATEGORY } from "./form.config";

const OPTIONS = Object.values(CATEGORY_OPTIONS);

const StyledIcon = styled.span``;
const StyledOptionLabel = styled.span``;
const StyledBox = styled.span``;

const StyledOption = styled(Card).attrs({
  as: "label",
})`
  position: relative;
  display: flex;
  flex-flow: row nowrap;
  align-items: center;
  margin-bottom: 0;
  padding: 1rem;
  gap: 1rem;
  color: ${(props) =>
    props.$disabled ? props.theme.black500 : props.theme.black1000};
  font-size: 1rem;

  @media (max-width: ${(props) => props.theme.collapse}px) {
    font-size: 0.875rem;
  }

  && {
    cursor: ${(props) => (props.$disabled ? "default" : "pointer")};
  }

  input {
    position: absolute;
    z-index: -1;
    opacity: 0;
  }

  ${StyledIcon} {
    flex: 0 0 3rem;
    width: 3rem;
    height: 3rem;
    border-radius: 100%;
    padding: 0;
    margin: 0;
    line-height: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    background-color: ${({ $disabled, theme }) =>
      $disabled ? theme.secondary100 : theme.secondary500};
  }

  ${StyledOptionLabel} {
    flex: 1 1 auto;
    font-weight: 400;
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
    border-radius: 100%;
    border-style: solid;
    border-width: 1px;
    border-color: ${(props) => {
      if (props.$checked && props.$disabled) {
        return props.theme.primary150;
      }
      if (props.$checked) {
        return props.theme.primary500;
      }
      if (props.$disabled) {
        return props.theme.black200;
      }
      return props.theme.black1000;
    }};
    background: ${(props) => {
      if (props.$checked && props.$disabled) {
        return `radial-gradient(circle, ${props.theme.primary150} 4px, ${props.theme.white} 5px, ${props.theme.white} 6px, ${props.theme.primary150} 7px)`;
      }
      if (props.$checked) {
        return `radial-gradient(circle, ${props.theme.primary500} 4px, ${props.theme.white} 5px, ${props.theme.white} 6px, ${props.theme.primary500} 7px)`;
      }
      if (props.$disabled) {
        return props.theme.black100;
      }
      return props.theme.white;
    }};
    transition: all 100ms ease-in;
  }

  &:hover ${StyledBox} {
    ${({ $checked, $disabled }) =>
      !$disabled && !$checked
        ? `background: ${(props) => props.theme.black50};`
        : ""};
  }

  input:focus + ${StyledBox} {
    box-shadow: ${(props) =>
      !props.$disabled ? `0 0 0 4px ${props.theme.primary100}` : "none"};
  }
`;

const StyledLabel = styled.div``;
const StyledHelpText = styled.div``;
const StyledOptions = styled.div``;
const StyledError = styled.div``;

const StyledField = styled.div`
  display: grid;
  align-items: stretch;
  grid-gap: 8px 0;
  font-size: 1rem;
  font-weight: 400;
  margin-bottom: 0;
  max-width: 100%;
  font-size: 0.875rem;
  line-height: 1.5;

  ${StyledLabel} {
    font-weight: 600;
  }

  ${StyledHelpText} {
    color: ${(props) => props.theme.black500};
    font-weight: 600;

    @media (max-width: ${(props) => props.theme.collapse}px) {
      font-weight: 400;
    }
  }

  ${StyledOptions} {
    margin-top: 0.5rem;
    display: grid;
    grid-auto-flow: column;
    grid-template-columns: repeat(2, 1fr);
    grid-template-rows: repeat(5, auto);
    gap: 0.5rem 1rem;
    width: 100%;

    @media (max-width: ${(props) => props.theme.collapse}px) {
      display: flex;
      flex-flow: column nowrap;
    }
  }

  ${StyledError} {
    display: flex;
    gap: 0.5rem;
    color: ${(props) => props.theme.redNSP};

    &:empty {
      display: none;
    }
  }
`;

const CategoryField = (props) => {
  const { id, onChange, value, label, error, disabled, ...rest } = props;

  const handleChange = useCallback(
    (e) => {
      onChange(e.target.value);
    },
    [onChange],
  );

  const options = useMemo(
    () =>
      value && !CATEGORY_OPTIONS[value]
        ? [
            ...OPTIONS,
            {
              ...FALLBACK_CATEGORY,
              value,
            },
          ]
        : OPTIONS,
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [],
  );

  return (
    <StyledField
      $valid={!error}
      $invalid={!!error}
      $empty={!!value}
      tabIndex="1"
    >
      {label && <StyledLabel>{label}</StyledLabel>}
      <StyledError style={{ color: "#EA610B" }}>
        <RawFeatherIcon width="1rem" height="1rem" name="alert-circle" />
        Attention, une demande de dépense correspond à une pièce comptable.
      </StyledError>
      <StyledHelpText>
        S’il y a plusieurs catégories pour une même pièce, choisissez la
        catégorie dont la valeur est la plus significative.
      </StyledHelpText>
      <StyledOptions id={id}>
        {options.map((option) => (
          <StyledOption
            key={option.value}
            htmlFor={id + "_" + option.value}
            $checked={value === option.value}
            $disabled={disabled}
            bordered
          >
            <StyledIcon>
              <RawFeatherIcon
                width="1.5rem"
                height="1.5rem"
                name={option.icon}
              />
            </StyledIcon>
            <StyledOptionLabel>{option.label}</StyledOptionLabel>
            <input
              {...rest}
              id={id + "_" + option.value}
              type="radio"
              onChange={handleChange}
              checked={value === option.value}
              value={option.value}
              disabled={disabled}
            />
            <StyledBox />
          </StyledOption>
        ))}
      </StyledOptions>
      <StyledError>{error}</StyledError>
    </StyledField>
  );
};

CategoryField.propTypes = {
  value: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
  onChange: PropTypes.func,
  id: PropTypes.string,
  name: PropTypes.string,
  label: PropTypes.node,
  disabled: PropTypes.bool,
  error: PropTypes.string,
};

export default CategoryField;
