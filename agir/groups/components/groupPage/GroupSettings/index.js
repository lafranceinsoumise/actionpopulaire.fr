import React from "react";

import ObjectManagement from "@agir/front/genericComponents/ObjectManagement";
import { MENU_ITEMS_GROUP, DEFAULT_GROUP } from "./mock-group.js";

export const GroupSettings = () => {
  return (
    <ObjectManagement object={DEFAULT_GROUP} menu_items={MENU_ITEMS_GROUP} />
  );
};
GroupSettings.propTypes = {};

export default GroupSettings;
