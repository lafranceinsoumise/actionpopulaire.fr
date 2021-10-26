import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";
import Avatar from "@agir/front/genericComponents/Avatar";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";
import Button from "@agir/front/genericComponents/Button";

const Name = styled.span``;
const Description = styled.span``;
const Label = styled.span``;
const StyledGroup = styled.div`
  cursor: ${({ isSelectGroup }) => (isSelectGroup ? "pointer" : "default")};
  background-color: ${style.white};
  padding: 0.75rem 1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  grid-gap: 0 1rem;

  @media (max-width: 444px) {
    flex-direction: column;
    align-items: start;
  }

  & > * {
    margin: 0;
  }

  ${Avatar}, ${RawFeatherIcon} {
    margin-right: 0.5rem;
  }

  ${Avatar} {
    grid-row: span 2;
    width: 2rem;
    height: 2rem;

    @media (max-width: ${style.collapse}px) {
      grid-row: span 3;
      width: 1.5rem;
      height: 1.5rem;
      align-self: start;
    }
  }

  ${RawFeatherIcon} {
    flex: 0 0 auto;
    display: flex;
    align-items: center;
    justify-content: center;
    width: 2rem;
    height: 2rem;
    background-color: ${style.primary500};
    color: #fff;
    clip-path: circle(1rem);
    text-align: center;
  }

  ${Name} {
    flex: 1 1 auto;
    font-weight: 500;
    min-width: 1px;
    text-overflow: ellipsis;
    white-space: nowrap;
    overflow: hidden;
  }

  ${Description} {
    display: block;
    color: ${style.black500};
    font-weight: 400;
    font-size: 0.875rem;
    text-overflow: ellipsis;
    white-space: nowrap;
    overflow: hidden;
  }

  ${Label} {
    font-size: 13px;
  }

  ${Button} {
    @media (max-width: 444px) {
      display: none;
    }
  }

  > div:first-child {
    opacity: ${({ disabled }) => (disabled ? 0.7 : 1)};
    display: flex;
    align-items: center;

    @media (min-width: ${style.collapse}px) {
      display: inline-flex;
    }
  }
  > div:last-child {
    align-items: center;
    display: block;
    text-align: right;
    width: 100%;

    @media (min-width: ${style.collapse}px) {
      display: inline-flex;
      justify-content: end;
    }
  }
`;

const GroupItem = ({
  id,
  name,
  image = "",
  description = "",
  selectGroup,
  label,
  disabled,
}) => {
  return (
    <StyledGroup
      disabled={disabled}
      isSelectGroup={!!selectGroup}
      onClick={() => selectGroup && selectGroup({ id, name, description })}
    >
      <div>
        {image ? (
          <Avatar image={image} name={name} />
        ) : (
          <RawFeatherIcon width="1rem" height="1rem" name="users" />
        )}
        <Name>
          {name}
          <Description>{description}</Description>
        </Name>
      </div>

      <div>
        {selectGroup && (
          <Button
            color="choose"
            small
            onClick={() => selectGroup({ id, name, description })}
          >
            Inviter
          </Button>
        )}
        {!!label && <Label>{label}</Label>}
      </div>
    </StyledGroup>
  );
};

GroupItem.propTypes = {
  id: PropTypes.string,
  name: PropTypes.string,
  image: PropTypes.string,
  description: PropTypes.string,
  selectGroup: PropTypes.func,
};

export default GroupItem;
