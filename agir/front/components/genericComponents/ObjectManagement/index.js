import React, { useState, useCallback, cloneElement } from "react";

import { useHistory } from "react-router-dom";
import { routeConfig } from "@agir/front/app/routes.config";

import PageFadeIn from "@agir/front/genericComponents/PageFadeIn";
import ManagementMenu from "@agir/front/genericComponents/ObjectManagement/ManagementMenu.js";
import ManagementPanel from "@agir/front/genericComponents/ObjectManagement/ManagementPanel.js";

export const ObjectManagement = (props) => {
  const { object, menu_items } = props;

  const history = useHistory();
  const firstItem = Object.keys(menu_items)[0];
  const [selectedItem, setSelectedItem] = useState(firstItem);
  const [showPanel, setShowPanel] = useState(true);

  const handleSelectMenuItem = useCallback((id) => {
    setShowPanel(true);
    setSelectedItem(id);
    // history.replace(routeConfig[menu_items[id].route].getLink());
    // history.replace(menu_items[id].route);
    // window.history.replaceState(null, id, menu_items[id].route);
  }, []);

  return (
    <PageFadeIn ready={true}>
      <ManagementMenu
        title={object.title}
        items={menu_items}
        selectedItem={selectedItem}
        onSelect={handleSelectMenuItem}
      />
      <ManagementPanel showPanel={showPanel}>
        {cloneElement(menu_items[selectedItem].component, {
          onBack: () => {
            setShowPanel(false);
          },
          illustration: menu_items[selectedItem].illustration,
          ...props,
        })}
      </ManagementPanel>
    </PageFadeIn>
  );
};
ObjectManagement.propTypes = {};

export default ObjectManagement;
