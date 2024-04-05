import React from "react";
import PropTypes from "prop-types";

import styled from "styled-components";
import * as style from "@agir/front/genericComponents/_variables.scss";

import GroupItem from "./GroupItem";
import ButtonAddList from "@agir/front/genericComponents/ObjectManagement/ButtonAddList.js";

const StyledList = styled.div`
  box-shadow: ${style.cardShadow};
  border-radius: 8px;
  overflow: hidden;

  & > * {
    border-bottom: 1px solid ${style.black50};
  }
`;

const GroupList = ({
  groups = [],
  children,
  onAdd,
  addButtonLabel,
  isLoading,
  selectGroup,
}) => (
  <StyledList>
    {groups.map((group) => {
      const description =
        !!group.type && !!group.location
          ? `${group.type} à ${group.location?.city} (${group.location?.zip})`
          : undefined;
      return (
        <GroupItem
          {...group}
          key={group.id}
          isLoading={isLoading}
          description={description}
          selectGroup={selectGroup}
        />
      );
    })}
    {children}
    {onAdd && addButtonLabel && (
      <ButtonAddList onClick={onAdd} label={addButtonLabel} />
    )}
  </StyledList>
);

GroupList.propTypes = {
  groups: PropTypes.arrayOf(PropTypes.shape(GroupItem.propTypes)),
  children: PropTypes.node,
  onAdd: PropTypes.func,
  addButtonLabel: PropTypes.node,
  isLoading: PropTypes.bool,
  selectGroup: PropTypes.func,
};

export default GroupList;
