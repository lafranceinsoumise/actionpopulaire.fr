import PropTypes from "prop-types";
import React, { useCallback, useEffect, useMemo, useState } from "react";
import { usePrevious } from "react-use";
import styled from "styled-components";

import RadioField from "@agir/front/formComponents/RadioField";

import { displayPrice } from "@agir/lib/utils/display";
import { getReminder, getAllocationOptions } from "./allocations.config";

const StyledError = styled.span`
  font-size: 13px;
  color: ${(props) => props.theme.redNSP};
`;

const StyledAllocationOption = styled.label`
  display: flex;
  height: 40px;
  align-items: center;
  margin: 0;
  padding: 0;
  font-size: 0.875rem;
  color: ${(props) =>
    props.$error
      ? props.theme.redNSP
      : props.$disabled
      ? props.theme.black500
      : props.theme.black1000};

  span {
    display: block;
    flex: 0 0 70px;
    height: 100%;
    position: relative;

    &::after {
      font-family: monospace;
      content: "€";
      position: absolute;
      right: 0.5rem;
      top: 50%;
      transform: translateY(-50%);
      font-weight: 400;
    }
  }

  input {
    color: inherit;
    display: block;
    height: 100%;
    width: 100%;
    padding-left: 0.5rem;
    padding-right: 1.5rem;
    text-align: right;
    font-weight: 400;
    height: 100%;
    border-radius: ${(props) => props.theme.borderRadius};
    border: 1px solid
      ${(props) => (props.$error ? props.theme.redNSP : props.theme.black100)};
    outline: none;
    -moz-appearance: textfield;

    &::-webkit-outer-spin-button,
    &::-webkit-inner-spin-button {
      -webkit-appearance: none;
      margin: 0;
    }

    &:focus {
      border: 1px solid
        ${(props) =>
          props.$error ? props.theme.redNSP : props.theme.black1000};
    }

    &:disabled,
    &:disabled:focus {
      background-color: ${(props) => props.theme.black100};
      border: 1px solid ${(props) => props.theme.black100};
    }
  }

  strong {
    flex: 1 1 auto;
    padding: 0 12px;
    font-weight: 600;
  }
`;

const StyledWidget = styled.div`
  margin: 2rem 0;

  fieldset {
    display: flex;
    flex-flow: column nowrap;
    gap: 0.5rem;
  }
`;

const AllocationWidget = (props) => {
  const { totalAmount, value, groupId, fixedRatio, error, disabled, onChange } =
    props;

  const previousTotalAmount = usePrevious(totalAmount);

  const [isCustom, setIsCustom] = useState(false);

  const options = useMemo(
    () => getAllocationOptions(totalAmount, groupId, fixedRatio),
    [totalAmount, groupId, fixedRatio]
  );

  const currentValue = useMemo(
    () =>
      value &&
      value.reduce(
        (obj, option) => ({ ...obj, [option.type]: option.value }),
        {}
      ),
    [value]
  );

  const remainder = useMemo(
    () => getReminder(currentValue, totalAmount),
    [currentValue, totalAmount]
  );

  const handleSelectOption = useCallback(
    (selected = "default") => {
      setIsCustom(selected === "custom");
      onChange(
        options.map((option) => ({
          ...option,
          value: option.defaultValue,
        }))
      );
    },
    [options, onChange]
  );

  const handleChange = useCallback(
    (e) => {
      const { name: type, value: newValue } = e.target;
      const newState = value.reduce(
        (obj, option) => ({
          ...obj,
          [option.type]: option,
        }),
        {}
      );
      newState[type].value = newValue;
      if (!isNaN(parseFloat(newState[type].value))) {
        newState[type].value = parseFloat(newState[type].value);
        newState[type].value = Math.abs(newState[type].value) * 100;
      }
      onChange(Object.values(newState));
    },
    [onChange, value]
  );

  useEffect(() => {
    if (!currentValue || totalAmount !== previousTotalAmount) {
      handleSelectOption();
    }
  }, [currentValue, totalAmount, previousTotalAmount, handleSelectOption]);

  if (!currentValue || totalAmount !== previousTotalAmount) {
    return null;
  }

  return (
    <StyledWidget>
      <RadioField
        small
        label="Je choisi la répartition de mon financement"
        options={[
          {
            value: "default",
            label: options.map((option) => (
              <span key={option.type} style={{ display: "block" }}>
                <strong>{displayPrice(option.defaultValue)}</strong>
                &nbsp;
                {option.label}
                {!!option.fixedRatio ? ` (${option.fixedRatio * 100}%)` : ""}
              </span>
            )),
          },
          { value: "custom", label: "Personnaliser" },
        ]}
        value={isCustom ? "custom" : "default"}
        onChange={handleSelectOption}
        disabled={disabled}
        error={error}
      />
      {isCustom && (
        <fieldset style={{ marginTop: "1rem" }}>
          {options.map(({ type, label, fixedRatio }) => (
            <StyledAllocationOption
              key={type}
              htmlFor={type}
              $disabled={disabled || !!fixedRatio}
              $error={!fixedRatio && remainder !== 0}
            >
              <span>
                <input
                  id={type}
                  name={type}
                  type="number"
                  min="0"
                  value={
                    currentValue
                      ? isNaN(parseInt(currentValue[type]))
                        ? currentValue[type]
                        : currentValue[type] / 100
                      : 0
                  }
                  onChange={handleChange}
                  disabled={disabled || !!fixedRatio}
                />
              </span>
              <strong>
                {label}
                {!!fixedRatio ? ` (${fixedRatio * 100}%)` : ""}
              </strong>
            </StyledAllocationOption>
          ))}
          {remainder !== 0 && (
            <StyledError>
              ⚠&nbsp;La somme des montants indiqués est différente du total :{" "}
              <strong>
                {displayPrice(Math.abs(remainder))}{" "}
                {remainder < 0 ? "en trop" : "en moins"}
              </strong>
            </StyledError>
          )}
        </fieldset>
      )}
    </StyledWidget>
  );
};

AllocationWidget.propTypes = {
  totalAmount: PropTypes.number,
  value: PropTypes.arrayOf(
    PropTypes.shape({
      type: PropTypes.string,
      value: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
    })
  ),
  groupId: PropTypes.string,
  fixedRatio: PropTypes.number,
  error: PropTypes.string,
  disabled: PropTypes.bool,
  onChange: PropTypes.func.isRequired,
};

export default AllocationWidget;
