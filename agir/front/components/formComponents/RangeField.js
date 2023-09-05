import { validProps } from "@agir/lib/utils/react";
import PropTypes from "prop-types";
import React, { useCallback, useMemo, useState } from "react";
import styled from "styled-components";

const StyledLabel = styled.div``;
const StyledRangeInput = styled.div`
  height: 100%;
  padding: 0 11px;
  display: flex;
  flex-flow: column nowrap;
  justify-content: center;
  align-items: stretch;
  border: 1px solid;
  border-color: ${(props) =>
    props.$invalid
      ? props.theme.redNSP
      : props.$focused
      ? props.theme.black500
      : props.theme.black100};
  outline-style: solid;
  outline-color: ${(props) =>
    props.$focused && props.$invalid
      ? props.theme.redNSP
      : props.theme.black500};
  outline-width: ${(props) => (props.$focused && props.$invalid ? 1 : 0)}px;

  input {
    color: ${(props) => props.theme.primary500};
    /* === range commons === */
    box-sizing: border-box;
    appearance: none;
    -webkit-appearance: none;
    margin: 0 auto;
    width: 100%;
    background: transparent;
    overflow: hidden;

    &:active {
      cursor: grabbing;
    }

    &,
    &:focus {
      border: none;
      outline: none;
      box-shadow: none;
    }

    &:disabled {
      color: ${(props) => props.theme.black500};
    }

    /* === WebKit specific styles === */
    &,
    &::-webkit-slider-runnable-track,
    &::-webkit-slider-thumb {
      -webkit-appearance: none;
      transition: all ease 100ms;
      height: 1rem;
    }

    &::-webkit-slider-runnable-track,
    &::-webkit-slider-thumb {
      position: relative;
    }

    &::-webkit-slider-thumb {
      --thumb-radius: 0.5rem - 1px;
      --clip-top: calc((1rem - 0.125rem) * 0.5 - 0.0313rem);
      --clip-bottom: calc(1rem - var(--clip-top));
      --clip-further: calc(100% + 1px);
      --box-fill: calc(-100vmax - 1rem) 0 0 100vmax currentColor;

      width: 1rem;
      background: linear-gradient(currentColor 0 0) scroll no-repeat left center /
        50% 0.1875rem;
      background-color: currentColor;
      box-shadow: var(--box-fill);
      border-radius: 1rem;
      clip-path: polygon(
        100% -1px,
        0.125em -1px,
        0 var(--clip-top),
        -100vmax var(--clip-top),
        -100vmax var(--clip-bottom),
        0 var(--clip-bottom),
        0.125em 100%,
        var(--clip-further) var(--clip-further)
      );
    }

    &:hover::-webkit-slider-thumb {
      cursor: grab;
    }

    &:active::-webkit-slider-thumb {
      cursor: grabbing;
    }

    &::-webkit-slider-runnable-track {
      border-radius: 0.5rem;
      background: linear-gradient(${(props) => props.theme.black200} 0 0) scroll
        no-repeat center / 100% calc(0.125rem + 1px);
    }

    &:disabled::-webkit-slider-thumb {
      cursor: not-allowed;
    }

    /* === Firefox specific styles === */
    &,
    &::-moz-range-track,
    &::-moz-range-thumb {
      appearance: none;
      transition: all ease 100ms;
      height: 1rem;
    }

    &::-moz-range-track,
    &::-moz-range-thumb,
    &::-moz-range-progress {
      background: #fff0;
    }

    &::-moz-range-thumb {
      background: currentColor;
      border: 0;
      width: 1rem;
      border-radius: 1rem;
      cursor: grab;
    }

    &:active::-moz-range-thumb {
      cursor: grabbing;
    }

    &::-moz-range-track {
      border-radius: 0.5rem;
      width: 100%;
      background: ${(props) => props.theme.black200};
    }

    &::-moz-range-progress {
      appearance: none;
      background: currentColor;
      transition-delay: 30ms;
    }

    &::-moz-range-track,
    &::-moz-range-progress {
      height: calc(0.125rem + 1px);
      border-radius: 0.125rem;
    }

    &:disabled::-moz-range-thumb {
      cursor: not-allowed;
    }
  }
`;
const StyledNumberInput = styled.div`
  position: relative;
  font-weight: 400;
  font-size: 1rem;
  line-height: 1.5;

  input {
    display: block;
    background-color: transparent;
    color: inherit;
    text-align: right;
    height: 100%;
    width: 100%;
    padding: 0.1rem 2.8rem 0rem 0.5rem;
    outline: none;
    -moz-appearance: textfield;
    border: 1px solid;
    border-color: ${(props) =>
      props.$invalid ? props.theme.redNSP : props.theme.black100};
    outline-color: ${(props) =>
      props.$invalid ? props.theme.redNSP : props.theme.black500};

    &:focus {
      outline-style: solid;
      outline-width: ${(props) => (props.$invalid ? 1 : 0)}px;
      border-color: ${(props) =>
        props.$invalid ? props.theme.redNSP : props.theme.black500};
    }

    &::-webkit-outer-spin-button,
    &::-webkit-inner-spin-button {
      -webkit-appearance: none;
      margin: 0;
    }
  }

  &::after {
    position: absolute;
    content: "Km";
    top: 50%;
    right: 1rem;
    transform: translateY(-50%);
    pointer-events: none;
  }
`;
const StyledHelpText = styled.div``;
const StyledError = styled.div``;

const StyledField = styled.div`
  display: grid;
  align-items: stretch;
  font-size: 0.875rem;
  font-weight: 400;
  line-height: 1;
  margin-bottom: 0;
  grid-template-columns: 1fr 6.25rem;
  grid-template-rows: auto 2.5rem;
  grid-auto-rows: auto;
  grid-gap: 0.25rem 0.5rem;

  & > * {
    grid-column: span 2;
  }

  ${StyledLabel} {
    font-weight: 400;
    font-size: 0.875rem;
    line-height: 1.5;
    margin-bottom: 0.25rem;
  }

  ${StyledHelpText} {
    line-height: 1.5;
  }

  ${StyledRangeInput}, ${StyledNumberInput} {
    grid-column: span 1;
    height: 100%;
    ${(props) => (props.$disabled ? `color: ${props.theme.black500};` : "")}
  }

  ${StyledRangeInput}, ${StyledNumberInput} input {
    border-radius: ${(props) => props.theme.softBorderRadius};
  }

  ${StyledError} {
    display: flex;
    color: ${(props) => props.theme.redNSP};

    &:empty {
      display: none;
    }
  }
`;

const RangeField = (props) => {
  const {
    id,
    onChange,
    value,
    min = 0,
    max = 100,
    step,
    label,
    error,
    helpText,
    disabled,
    className,
    style,
    ...rest
  } = props;

  const [rangeFocused, setRangeFocused] = useState(false);

  const handleRangeFocus = useCallback(() => {
    setRangeFocused(true);
  }, []);

  const handleRangeBlur = useCallback(() => {
    setRangeFocused(false);
  }, []);

  const handleChange = useCallback(
    (e) => {
      onChange(e.target.value);
    },
    [onChange]
  );

  const inputProps = useMemo(() => validProps(rest), [rest]);

  return (
    <StyledField
      tabIndex="1"
      title={`Veuillez choisir une valeur entre ${min} et ${max}`}
      className={className}
      style={style}
    >
      {label && <StyledLabel htmlFor={id}>{label}</StyledLabel>}
      <StyledRangeInput
        $invalid={!!error}
        $disabled={!!disabled}
        $focused={!!rangeFocused}
        onClick={handleRangeFocus}
      >
        <input
          type="range"
          onChange={handleChange}
          onFocus={handleRangeFocus}
          onBlur={handleRangeBlur}
          value={value || min}
          min={min}
          max={max}
          step={step}
          disabled={disabled}
          aria-hidden={true}
          title={value}
        />
      </StyledRangeInput>
      <StyledNumberInput $invalid={!!error}>
        <input
          {...inputProps}
          id={id}
          type="number"
          onChange={handleChange}
          value={value}
          min={min}
          max={max}
          step={step}
          disabled={disabled}
        />
      </StyledNumberInput>
      {helpText && <StyledHelpText>{helpText}</StyledHelpText>}
      <StyledError>{error}</StyledError>
    </StyledField>
  );
};

RangeField.propTypes = {
  onChange: PropTypes.func,
  value: PropTypes.oneOfType([PropTypes.number, PropTypes.string]),
  min: PropTypes.number,
  max: PropTypes.number,
  step: PropTypes.number,
  id: PropTypes.string,
  name: PropTypes.string,
  label: PropTypes.node,
  disabled: PropTypes.bool,
  error: PropTypes.string,
  helpText: PropTypes.node,
  className: PropTypes.string,
  style: PropTypes.object,
};

export default RangeField;
