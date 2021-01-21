import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";

const StyledButton = styled.button`
  border: none;
  margin: 0;
  text-decoration: none;
  background-color: ${style.black50};
  cursor: pointer;
  text-align: center;
  -webkit-appearance: none;
  -moz-appearance: none;
  color: ${style.black1000};
  border-radius: 3px;
  display: block;
  width: 100%;
  height: 54px;
  padding: 0.5rem;

  &:focus,
  &:hover {
    border: none;
    outline: none;
    opacity: 0.8;
  }

  & > span {
    display: flex;
    flex-flow: row nowrap;
    align-items: center;
    background-color: white;
    padding: 0 18px;
    height: 100%;
    border: 1px solid ${style.black100};
    font-size: 0.875rem;
    font-weight: 400;

    span {
      text-overflow: ellipsis;
      white-space: nowrap;
      overflow: hidden;
    }

    ${RawFeatherIcon} {
      width: 1rem;
      height: 1rem;
      margin-right: 12px;
    }
  }
`;

const Trigger = (props) => {
  const { user, onClick } = props;

  return (
    <StyledButton onClick={onClick}>
      <span>
        <RawFeatherIcon name="edit-2" />
        <span>
          {user.fullName.split(" ")[0]}, publiez un message dans votre groupe
        </span>
      </span>
    </StyledButton>
  );
};
Trigger.propTypes = {
  onClick: PropTypes.func.isRequired,
  user: PropTypes.shape({
    fullName: PropTypes.string.isRequired,
  }).isRequired,
};
export default Trigger;
