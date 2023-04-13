import PropTypes from "prop-types";
import React, { useCallback } from "react";
import styled from "styled-components";

const StyledLabel = styled.div``;
const StyledRange = styled.input`
  color: ${(props) => props.theme.primary500};
  --brightness-hover: 110%;
  --brightness-down: 90%;

  /* === range commons === */
  box-sizing: border-box;
  height: 2.5rem;
  padding: 0.6875rem;
  -webkit-appearance: none;
  margin: 0 auto;
  width: 100%;
  background: transparent;
  overflow: hidden;

  &:active {
    cursor: grabbing;
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
    --thumb-radius: 0.5rem - 0.0625rem;
    --clip-top: calc((1rem - 0.125rem) * 0.5 - 0.0313rem);
    --clip-bottom: calc(1rem - var(--clip-top));
    --clip-further: calc(100% + 0.0625rem);
    --box-fill: calc(-100vmax - 1rem) 0 0 100vmax currentColor;

    width: 1rem;
    background: linear-gradient(currentColor 0 0) scroll no-repeat left center /
      50% 0.1875rem;
    background-color: currentColor;
    box-shadow: var(--box-fill);
    border-radius: 1rem;
    filter: brightness(100%);
    clip-path: polygon(
      100% -0.0625rem,
      0.125em -0.0625rem,
      0 var(--clip-top),
      -100vmax var(--clip-top),
      -100vmax var(--clip-bottom),
      0 var(--clip-bottom),
      0.125em 100%,
      var(--clip-further) var(--clip-further)
    );
  }

  &:hover::-webkit-slider-thumb {
    filter: brightness(var(--brightness-hover));
    cursor: grab;
  }

  &:active::-webkit-slider-thumb {
    filter: brightness(var(--brightness-down));
    cursor: grabbing;
  }

  &::-webkit-slider-runnable-track {
    border-radius: 0.5rem;
    background: linear-gradient(${(props) => props.theme.black200} 0 0) scroll
      no-repeat center / 100% calc(0.125rem + 0.0625rem);
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
    height: calc(0.125rem + 0.0625rem);
    border-radius: 0.125rem;
  }

  &::-moz-range-thumb,
  &::-moz-range-progress {
    filter: brightness(100%);
  }

  &:hover::-moz-range-thumb,
  &:hover::-moz-range-progress {
    filter: brightness(var(--brightness-hover));
  }

  &:active::-moz-range-thumb,
  &:active::-moz-range-progress {
    filter: brightness(var(--brightness-down));
  }

  &:disabled::-moz-range-thumb {
    cursor: not-allowed;
  }
`;
const StyledNumberInput = styled.div`
  position: relative;
  font-weight: 400;
  font-size: 1rem;
  line-height: 1.5;

  input {
    display: block;
    color: inherit;
    text-align: right;
    height: 100%;
    width: 100%;
    padding: 0.5rem;
    padding-right: 2.8rem;
    outline: none;
    -moz-appearance: textfield;

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
  }

  ${StyledHelpText} {
    line-height: 1.5;
  }

  ${StyledRange}, ${StyledNumberInput} {
    grid-column: span 1;
    height: 100%;
    ${(props) => (props.$disabled ? `color: ${props.theme.black500};` : "")}
  }

  input {
    border-radius: ${(props) => props.theme.softBorderRadius};
    border: 1px solid
      ${(props) => (props.$invalid ? props.theme.redNSP : props.theme.black100)};
    outline: none;

    &:focus {
      outline: none;
      border: ${(props) => (props.$invalid ? 2 : 1)}px solid
        ${(props) =>
          props.$invalid ? props.theme.redNSP : props.theme.black500};
    }
  }

  ${StyledError} {
    display: ${({ $invalid }) => ($invalid ? "flex" : "none")};
    color: ${(props) => props.theme.redNSP};
  }
`;

const RangeField = (props) => {
  const {
    id,
    onChange,
    value,
    min = 0,
    max = 100,
    step = 1,
    label,
    error,
    helpText,
    disabled,
    ...rest
  } = props;

  const handleChange = useCallback(
    (e) => {
      onChange(e.target.value);
    },
    [onChange]
  );

  return (
    <StyledField
      $valid={!error}
      $invalid={!!error}
      $empty={!!value}
      $disabled={!!disabled}
      tabIndex="1"
      title={`Veuillez choisir une valeur entre ${min} et ${max}`}
    >
      {label && <StyledLabel htmlForm={id}>{label}</StyledLabel>}
      <StyledRange
        {...rest}
        type="range"
        onChange={handleChange}
        value={value || min}
        min={min}
        max={max}
        step={step}
        disabled={disabled}
        aria-hidden={true}
        title={value}
      />
      <StyledNumberInput>
        <input
          id={id}
          type="number"
          onChange={handleChange}
          value={value || min}
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
  onChange: PropTypes.func.isRequired,
  value: PropTypes.oneOfType([PropTypes.number, PropTypes.string]),
  min: PropTypes.number,
  max: PropTypes.number,
  step: PropTypes.number,
  id: PropTypes.string,
  name: PropTypes.string,
  label: PropTypes.node,
  disabled: PropTypes.bool,
  error: PropTypes.string,
  helpText: PropTypes.string,
};

export default RangeField;
