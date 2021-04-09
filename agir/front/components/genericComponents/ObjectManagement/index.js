import React, { useState } from "react";

import PageFadeIn from "@agir/front/genericComponents/PageFadeIn";
import ManagementMenu from "@agir/front/genericComponents/ObjectManagement/ManagementMenu.js";
import ManagementPanel from "@agir/front/genericComponents/ObjectManagement/ManagementPanel.js";

export const ObjectManagement = (props) => {
  const { object, menu_items } = props;

  const firstItem = Object.keys(menu_items)[0];
  const [selectedItem, setSelectedItem] = useState(firstItem);
  const [showPanel, setShowPanel] = useState(true);

  const handleSelectMenuItem = (id) => {
    setShowPanel(true);
    setSelectedItem(id);
  };

  return (
    <PageFadeIn ready={true}>
      <ManagementMenu
        title={object.title}
        items={menu_items}
        selectedItem={selectedItem}
        onSelect={handleSelectMenuItem}
      />
      <ManagementPanel
        onBack={() => setShowPanel(false)}
        illustration={menu_items[selectedItem].illustration}
        showPanel={showPanel}
      >
        {menu_items[selectedItem].component}
      </ManagementPanel>
    </PageFadeIn>
  );
};
ObjectManagement.propTypes = {};

export default ObjectManagement;
