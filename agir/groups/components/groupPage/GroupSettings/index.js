import React from "react";

import ObjectManagement from "@agir/front/genericComponents/ObjectManagement";
import { MENU_ITEMS_GROUP } from "./group_items.js";

import { useGroup } from "@agir/groups/groupPage/hooks/group.js";

export const GroupSettings = (props) => {
  const { groupPk } = props;
  const group = useGroup(groupPk);

  return (
    <ObjectManagement object={group} menu_items={MENU_ITEMS_GROUP} {...props} />
  );
};
GroupSettings.propTypes = {};

export default GroupSettings;
