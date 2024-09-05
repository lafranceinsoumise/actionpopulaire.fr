import _sortBy from "lodash/sortBy";
import PropTypes from "prop-types";
import React, { useMemo } from "react";
import styled from "styled-components";

import EventMember from "./EventMember";
import ButtonAddList from "@agir/front/genericComponents/ObjectManagement/ButtonAddList.js";

const MemberList = styled.div`
  box-shadow: ${(props) => props.theme.cardShadow};
  border-radius: 8px;
  overflow: hidden;

  & > * {
    border-bottom: 1px solid ${(props) => props.theme.text50};
  }
`;

const EventMemberList = ({ members, onAdd, addButtonLabel, isLoading }) => {
  const list = useMemo(
    () =>
      Array.isArray(members) ? _sortBy(members, "isOrganizer").reverse() : [],
    [members],
  );

  return (
    <MemberList>
      {list.map((member) => (
        <EventMember key={member.id} isLoading={isLoading} {...member} />
      ))}
      {onAdd && addButtonLabel && (
        <ButtonAddList onClick={onAdd} label={addButtonLabel} />
      )}
    </MemberList>
  );
};
EventMemberList.propTypes = {
  members: PropTypes.arrayOf(PropTypes.shape(EventMember.propTypes)),
  onAdd: PropTypes.func,
  addButtonLabel: PropTypes.node,
  isLoading: PropTypes.bool,
};

export default EventMemberList;
