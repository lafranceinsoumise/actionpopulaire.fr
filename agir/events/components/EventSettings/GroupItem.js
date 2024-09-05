import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import Avatar from "@agir/front/genericComponents/Avatar";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";
import Button from "@agir/front/genericComponents/Button";
import Link from "@agir/front/app/Link";

const Name = styled.span``;
const Label = styled.span``;
const StyledGroup = styled.div`
  cursor: ${({ $isSelectGroup }) => ($isSelectGroup ? "pointer" : "default")};
  background-color: ${(props) => props.theme.background0};
  padding: 0.75rem 1rem;
  display: flex;
  flex-direction: column;

  & > * {
    margin: 0;
  }

  > div:first-child {
    opacity: ${({ disabled }) => (disabled ? 0.7 : 1)};
    display: flex;
    align-items: center;
    overflow: hidden;
    width: 100%;

    @media (min-width: ${(props) => props.theme.collapse}px) {
      display: inline-flex;
    }
  }

  > div:last-child {
    display: block;

    @media (min-width: ${(props) => props.theme.collapse}px) {
      display: inline-flex;
      align-items: center;
    }
  }

  ${Avatar}, ${RawFeatherIcon} {
    margin-right: 0.5rem;
  }

  ${Avatar} {
    grid-row: span 2;
    width: 2rem;
    height: 2rem;

    @media (max-width: ${(props) => props.theme.collapse}px) {
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
    background-color: ${(props) => props.theme.primary500};
    color: ${(props) => props.theme.background0};
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

    a {
      color: inherit;
    }
  }

  ${Label} {
    display: block;
    padding-left: 40px;
    font-size: 13px;
  }

  ${Button} {
    @media (max-width: ${(props) => props.theme.collapse}px) {
      display: none;
    }
  }
`;

const GroupItem = ({
  id,
  name,
  image = "",
  selectGroup,
  label,
  disabled,
  isLinked,
}) => (
  <StyledGroup
    disabled={disabled}
    $isSelectGroup={!!selectGroup}
    onClick={() => selectGroup && selectGroup({ id, name })}
  >
    <div>
      {image ? (
        <Avatar image={image} name={name} />
      ) : (
        <RawFeatherIcon width="1rem" height="1rem" name="users" />
      )}
      <Name>
        {!isLinked ? (
          name
        ) : (
          <Link route="groupDetails" routeParams={{ groupPk: id }}>
            {name}
          </Link>
        )}
      </Name>
      {selectGroup && (
        <Button color="choose" small onClick={() => selectGroup({ id, name })}>
          Inviter
        </Button>
      )}
    </div>
    <div>{!!label && <Label>{label}</Label>}</div>
  </StyledGroup>
);

GroupItem.propTypes = {
  id: PropTypes.string,
  name: PropTypes.string,
  image: PropTypes.string,
  selectGroup: PropTypes.func,
  label: PropTypes.string,
  disabled: PropTypes.bool,
  isLinked: PropTypes.bool,
};

export default GroupItem;
