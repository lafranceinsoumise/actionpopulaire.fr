import PropTypes from "prop-types";
import React, { useCallback, useEffect, useState } from "react";
import styled from "styled-components";

import RadioField from "@agir/front/formComponents/RadioField";

const DEFAULT_OPTIONS = [
  { value: 60, label: "60% au groupe d’action, 40% aux activités nationales" },
  { value: 85, label: "85% au groupe d’action, 15% aux activités nationales" },
  { value: 100, label: "100% au groupe d’action" },
  { value: "...", label: "Personnaliser" },
];

const StyledWidget = styled.div`
  margin: 2rem 0;

  fieldset {
    margin: 1rem 0 0;

    label {
      display: flex;
      height: 40px;
      align-items: center;
      margin: 0;
      padding: 0;

      span {
        display: block;
        flex: 0 0 70px;
        height: 100%;
        position: relative;

        &::after {
          content: "%";
          position: absolute;
          right: 0.5rem;
          top: 50%;
          transform: translateY(-50%);
          font-weight: 400;
        }
      }

      input {
        display: block;
        height: 100%;
        width: 100%;
        padding-left: 0.5rem;
        padding-right: 1.5rem;
        text-align: right;
        font-weight: 400;
        height: 100%;
        border-radius: ${(props) => props.theme.borderRadius};
        border: 1px solid ${(props) => props.theme.black100};
        outline: none;
        -moz-appearance: textfield;

        &::-webkit-outer-spin-button,
        &::-webkit-inner-spin-button {
          -webkit-appearance: none;
          margin: 0;
        }

        &:focus {
          border-color: ${(props) => props.theme.black1000};
        }
      }

      strong {
        flex: 1 1 auto;
        padding: 0 12px;
        font-weight: 600;
      }
    }

    label + label {
      margin-top: 0.5rem;
    }
  }
`;

const GroupPercentageWidget = (props) => {
  const { value, onChange, disabled } = props;

  const [hasCustomAmount, setHasCustomAmount] = useState(
    !!value &&
      !DEFAULT_OPTIONS.some((option) => String(option.value) === String(value)),
  );

  const selectedOption =
    typeof value === "undefined"
      ? DEFAULT_OPTIONS[0]
      : hasCustomAmount
        ? DEFAULT_OPTIONS[DEFAULT_OPTIONS.length - 1]
        : DEFAULT_OPTIONS.find(
            (option) => String(option.value) === String(value),
          );

  const nationalPercentage = 100 - value;

  const handleSelectOption = useCallback(
    (selectedValue) => {
      if (!isNaN(parseInt(selectedValue))) {
        setHasCustomAmount(false);
        onChange(parseInt(selectedValue));
      } else {
        setHasCustomAmount(true);
        onChange(50);
      }
    },
    [onChange],
  );

  const handleGroupChange = useCallback(
    (e) => {
      let { value } = e.target;
      value = parseInt(value);
      if (isNaN(value)) {
        return;
      }
      value = Math.abs(value);
      value = Math.min(value, 100);
      value = Math.max(value, 0);
      onChange(value);
    },
    [onChange],
  );

  const handleNationalChange = useCallback(
    (e) => {
      let { value } = e.target;
      value = parseInt(value);
      if (isNaN(value)) {
        return;
      }
      value = Math.abs(value);
      value = Math.min(value, 100);
      value = Math.max(value, 0);
      onChange(100 - value);
    },
    [onChange],
  );

  useEffect(() => {
    typeof value === "undefined" && onChange(DEFAULT_OPTIONS[0].value);
  }, [value, onChange]);

  return (
    <StyledWidget style={{ margin: "2rem 0" }}>
      <RadioField
        small
        label="J’aide au financement des activités nationales"
        options={DEFAULT_OPTIONS}
        value={selectedOption.value}
        onChange={handleSelectOption}
        disabled={disabled}
      />
      {hasCustomAmount ? (
        <fieldset>
          <label htmlFor="groupPercentage">
            <span>
              <input
                name="groupPercentage"
                id="groupPercentage"
                type="number"
                step="1"
                min="0"
                max="100"
                value={value}
                onChange={handleGroupChange}
                disabled={disabled}
              />
            </span>
            <strong>Groupe d’action</strong>
          </label>
          <label htmlFor="nationalPercentage">
            <span>
              <input
                name="nationalPercentage"
                id="nationalPercentage"
                type="number"
                step="1"
                min="0"
                max="100"
                value={nationalPercentage}
                onChange={handleNationalChange}
                disabled={disabled}
              />
            </span>
            <strong>Activités nationales</strong>
          </label>
        </fieldset>
      ) : null}
    </StyledWidget>
  );
};

GroupPercentageWidget.propTypes = {
  value: PropTypes.number,
  onChange: PropTypes.func,
  disabled: PropTypes.bool,
};

export default GroupPercentageWidget;
