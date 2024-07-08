import _sortBy from "lodash/sortBy";
import PropTypes from "prop-types";
import React, { useCallback, useMemo, useState } from "react";
import styled from "styled-components";

import ButtonAddList from "@agir/front/genericComponents/ObjectManagement/ButtonAddList";
import SelectField from "@agir/front/formComponents/SelectField";
import Spacer from "@agir/front/genericComponents/Spacer";
import TextField from "@agir/front/formComponents/TextField";

import GroupMember from "./GroupMember";

const StyledControls = styled.div`
  padding: 1rem;
  display: flex;

  @media (max-width: ${(props) => props.theme.collapse}px) {
    display: block;
  }

  &:empty {
    display: none;
  }

  & > label {
    flex: 1 1 50%;

    & > span {
      font-size: 0.875rem;
    }
  }
`;

const MemberList = styled.div`
  box-shadow: ${(props) => props.theme.cardShadow};
  border-radius: ${(props) => props.theme.borderRadius};

  & > * {
    background-color: transparent;
    outline: none;
    border: none;
    border-bottom: 1px solid ${(props) => props.theme.text50};

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

const SORTING_OPTIONS = [
  {
    label: "---",
    value: "default",
    sortingFn: (members) => _sortBy(members, "membershipType").reverse(),
  },
  {
    label: "Ordre alphabétique",
    value: "alpha",
    sortingFn: (members) => _sortBy(members, "displayName"),
  },
  {
    label: "Arrivée dans le groupe",
    value: "created",
    sortingFn: (members) => _sortBy(members, "created"),
  },
];

const GroupMemberList = ({
  members,
  onAdd,
  onClickMember,
  addButtonLabel,
  isLoading,
  sortable,
  searchable,
}) => {
  const [search, setSearch] = useState("");
  const [sort, setSort] = useState(SORTING_OPTIONS[0]);

  const list = useMemo(() => {
    if (!Array.isArray(members)) {
      return [];
    }
    let result = members;
    if (search) {
      const searchTerm = search.toLowerCase();
      result = members.filter(
        ({ displayName, email }) =>
          displayName.toLowerCase().includes(searchTerm) ||
          email.toLowerCase().includes(searchTerm),
      );
    }
    if (members.length < 3) {
      return members;
    }
    return sort.sortingFn(result);
  }, [members, sort, search]);

  const handleSearch = useCallback((e) => {
    setSearch(e.target.value);
  }, []);

  return (
    <MemberList>
      {Array.isArray(members) && members.length >= 3 && (
        <StyledControls>
          {searchable && (
            <TextField
              label="Filter"
              value={search}
              onChange={handleSearch}
              placeholder="Filtrer par nom ou e-mail"
            />
          )}
          {sortable && searchable && <Spacer size="0.5rem" />}
          {sortable && (
            <SelectField
              label="Trier par..."
              value={sort}
              onChange={setSort}
              options={SORTING_OPTIONS}
            />
          )}
        </StyledControls>
      )}

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
  sortable: PropTypes.bool,
  searchable: PropTypes.bool,
};

export default GroupMemberList;
