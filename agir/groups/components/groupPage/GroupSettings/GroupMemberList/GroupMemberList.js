import _sortBy from "lodash/sortBy";
import PropTypes from "prop-types";
import React, { useMemo } from "react";
import styled from "styled-components";

import GroupMember from "./GroupMember";
import ButtonAddList from "@agir/front/genericComponents/ObjectManagement/ButtonAddList";

const MemberList = styled.div`
  box-shadow: ${(props) => props.theme.cardShadow};
  border-radius: ${(props) => props.theme.borderRadius};

  & > * {
    background-color: transparent;
    outline: none;
    border: none;
    border-bottom: 1px solid ${(props) => props.theme.black50};

    &:first-child {
      border-radius: ${(props) => props.theme.borderRadius}
        ${(props) => props.theme.borderRadius} 0 0;
    }
    &:last-child {
      border-radius: 0 0 ${(props) => props.theme.borderRadius}
        ${(props) => props.theme.borderRadius};
    }
    &:only-child {
      border-radius: ${(props) => props.theme.borderRadius};
    }
  }
`;

const GroupMemberList = ({
  members,
  onAdd,
  onClickMember,
  addButtonLabel,
  isLoading,
}) => {
  const list = useMemo(
    () =>
      Array.isArray(members)
        ? _sortBy(members, "membershipType").reverse()
        : [],
    [members]
  );

  return (
    <MemberList>
      {list.map((member) => (
        <GroupMember
          key={member.id}
          isLoading={isLoading}
          onClick={onClickMember}
          {...member}
        />
      ))}
      {onAdd && addButtonLabel && (
        <ButtonAddList onClick={onAdd} label={addButtonLabel} />
      )}
    </MemberList>
  );
};
GroupMemberList.propTypes = {
  members: PropTypes.arrayOf(PropTypes.shape(GroupMember.propTypes)),
  onAdd: PropTypes.func,
  onClickMember: PropTypes.func,
  addButtonLabel: PropTypes.node,
  isLoading: PropTypes.bool,
};

export default GroupMemberList;
