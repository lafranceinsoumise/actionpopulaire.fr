import React from "react";
import PropTypes from "prop-types";

import styled from "styled-components";
import style from "@agir/front/genericComponents/_variables.scss";

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
  groups,
  onAdd,
  addButtonLabel,
  isLoading,
  handleAction,
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
          handleAction={handleAction}
        />
      );
    })}
    {onAdd && addButtonLabel && (
      <ButtonAddList onClick={onAdd} label={addButtonLabel} />
    )}
  </StyledList>
);

GroupList.propTypes = {
  groups: PropTypes.arrayOf(PropTypes.shape(GroupItem.propTypes)),
  onAdd: PropTypes.func,
  addButtonLabel: PropTypes.node,
  isLoading: PropTypes.bool,
  handleAction: PropTypes.func,
};

export default GroupList;
