import React, { useState, useCallback, cloneElement } from "react";

import { useHistory } from "react-router-dom";

import ManagementMenu from "@agir/front/genericComponents/ObjectManagement/ManagementMenu.js";
import ManagementPanel from "@agir/front/genericComponents/ObjectManagement/ManagementPanel.js";

import { useIsDesktop } from "@agir/front/genericComponents/grid";

export const ObjectManagement = (props) => {
  const { object, menu_items, route, selected_item = null } = props;

  const history = useHistory();

  const isDesktop = useIsDesktop();
  const firstItem = Object.keys(menu_items)[0];
  const [selectedItem, setSelectedItem] = useState(selected_item || firstItem);
  const [showPanel, setShowPanel] = useState(!!selected_item || isDesktop);

  const handleSelectMenuItem = useCallback(
    (id) => {
      setShowPanel(true);
      setSelectedItem(id);

      const selected_route = menu_items[id].route;
      history.push(selected_route.replace(/:groupPk/, object.id));
    },
    [object]
  );

  return (
    <>
      <ManagementMenu
        title={object?.name}
        items={menu_items}
        selectedItem={selectedItem}
        onSelect={handleSelectMenuItem}
      />
      <ManagementPanel showPanel={showPanel}>
        {cloneElement(menu_items[selectedItem].component, {
          onBack: () => {
            setShowPanel(false);
            history.push(route.replace(/:groupPk/, object.id));
          },
          illustration: menu_items[selectedItem].illustration,
          ...props,
        })}
      </ManagementPanel>
    </>
  );
};
ObjectManagement.propTypes = {};

export default ObjectManagement;
