import React from "react";
import PropTypes from "prop-types";
import styled from "styled-components";

import { FlexContainer } from "./elements";

const TypeButton = styled.button`
  display: block;
  margin: 10px;
  font-weight: bold;
  min-width: 200px;
  padding: 1em;
  border-radius: 10px;

  &:disabled,
  &:disabled:focus {
    color: white;
    background-color: #01b1d4;
    opacity: 1;
    cursor: pointer;
  }
  &:disabled:hover {
    background-color: #0098b6;
    color: white;
  }
`;

const TypeWidget = ({ typeChoices, type, onTypeChange }) => (
  <FlexContainer justifyContent="center">
    {typeChoices.map(({ label, value, icon }) => (
      <TypeButton
        key={value}
        type="button"
        onClick={() => onTypeChange(value)}
        className="btn btn-default"
        disabled={type === value}
      >
        <div>
          <i className={`fa fa-${icon || "arrow-right"}`} />
        </div>
        <div>{label}</div>
      </TypeButton>
    ))}
  </FlexContainer>
);

TypeWidget.propTypes = {
  type: PropTypes.string,
  typeChoices: PropTypes.arrayOf(
    PropTypes.shape({
      value: PropTypes.string,
      label: PropTypes.string
    }).isRequired
  ),
  onTypeChange: PropTypes.func
};

export default TypeWidget;
