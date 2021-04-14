import React from "react";

import ObjectManagement from "@agir/front/genericComponents/ObjectManagement";
import { MENU_ITEMS_GROUP, DEFAULT_GROUP } from "./group_items.js";

export const GroupSettings = (props) => {
  return (
    <ObjectManagement
      object={DEFAULT_GROUP}
      menu_items={MENU_ITEMS_GROUP}
      {...props}
    />
  );
};
GroupSettings.propTypes = {};

export default GroupSettings;
