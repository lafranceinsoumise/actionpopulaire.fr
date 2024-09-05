import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

const StyledButton = styled.button`
  color: ${(props) => props.theme.primary500};
  background-color: transparent;
  border: none;
  font-weight: bold;
  font-size: 14px;
  line-height: 1.4;
  cursor: pointer;
  padding: 0;

  &:hover,
  &:focus {
    text-decoration: underline;
    cursor: pointer;
  }
`;

const ExpandButton = (props) => {
  const { onClick, disabled, label } = props;
  return (
    <StyledButton
      onClick={onClick}
      disabled={disabled}
      icon="chevron-down"
      rightIcon
    >
      {label}
    </StyledButton>
  );
};
ExpandButton.propTypes = {
  onClick: PropTypes.func.isRequired,
  disabled: PropTypes.bool,
  label: PropTypes.string,
};
ExpandButton.defaultProps = {
  disabled: false,
  label: "Voir plus",
};
export default ExpandButton;
