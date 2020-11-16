import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";
import FeatherIcon from "@agir/front/genericComponents/FeatherIcon";

const StyledButton = styled.button`
  color: ${style.primary500};
  background-color: transparent;
  border: none;
  font-weight: bold;
  font-size: 16px;
  line-height: 1.4;
  cursor: pointer;

  &:hover,
  &:focus {
    text-decoration: underline;
    cursor: pointer;
  }
`;

const ExpandButton = (props) => {
  const { onClick, disabled } = props;
  return (
    <StyledButton onClick={onClick} disabled={disabled}>
      Voir plus&nbsp;
      <FeatherIcon name="chevron-down" small inline />
    </StyledButton>
  );
};
ExpandButton.propTypes = {
  onClick: PropTypes.func.isRequired,
  disabled: PropTypes.bool,
};
ExpandButton.defaultProps = {
  disabled: false,
};
export default ExpandButton;
