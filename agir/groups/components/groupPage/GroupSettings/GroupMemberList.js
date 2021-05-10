import _sortBy from "lodash/sortBy";
import PropTypes from "prop-types";
import React, { useMemo } from "react";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

import GroupMember from "./GroupMember";
import AddPair from "./AddPair";

const MemberList = styled.div`
  box-shadow: ${style.cardShadow};
  border-radius: 8px;
  overflow: hidden;

  & > * {
    border-bottom: 1px solid ${style.black50};
  }
`;

const GroupMemberList = ({ members, onAdd, addButtonLabel, isLoading }) => {
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
        <GroupMember key={member.id} isLoading={isLoading} {...member} />
      ))}
      {onAdd && addButtonLabel && (
        <AddPair onClick={onAdd} label={addButtonLabel} />
      )}
    </MemberList>
  );
};
GroupMemberList.propTypes = {
  members: PropTypes.arrayOf(PropTypes.shape(GroupMember.propTypes)),
  onAdd: PropTypes.func,
  addButtonLabel: PropTypes.node,
  isLoading: PropTypes.bool,
};

export default GroupMemberList;
