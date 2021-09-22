import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";
import Avatar from "@agir/front/genericComponents/Avatar";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";
import Button from "@agir/front/genericComponents/Button";

const Name = styled.span``;
const Description = styled.span``;
const StyledGroup = styled.div`
  background-color: ${style.white};
  padding: 0.75rem 1rem;
  display: grid;
  grid-template-columns: auto 1fr auto;
  grid-template-rows: auto auto;
  align-items: center;
  grid-gap: 0 1rem;

  @media (max-width: ${style.collapse}px) {
    grid-template-columns: auto 1fr;
    grid-template-rows: auto auto auto;
  }

  & > * {
    margin: 0;
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
`;

const GroupItem = ({ id, name, image = "", description = "", selectGroup }) => {
  return (
    <StyledGroup>
      {image ? (
        <Avatar image={image} name={name} />
      ) : (
        <RawFeatherIcon width="1rem" height="1rem" name="users" />
      )}
      <Name>
        {name}
        <Description>{description}</Description>
      </Name>

      {selectGroup && (
        <Button
          color="choose"
          small
          onClick={() => selectGroup({ id, name, description })}
        >
          Inviter
        </Button>
      )}
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
